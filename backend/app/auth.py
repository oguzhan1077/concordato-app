from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from jose import JWTError, jwt
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
import os
import time
from . import models, schemas, security, database

router = APIRouter()

ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax").lower()
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
ACCESS_TOKEN_MAX_AGE = security.ACCESS_TOKEN_EXPIRE_MINUTES * 60
REFRESH_TOKEN_MAX_AGE = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


def _get_redis_connection():
    return redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


def _set_cookie(response: Response, key: str, value: str, max_age: int):
    # Cross-domain cookie için domain belirtilmemeli (None olmalı)
    # Eğer COOKIE_DOMAIN ayarlanmışsa ve cross-domain çalışmıyorsa None yap
    cookie_domain = None if COOKIE_DOMAIN else None  # Her zaman None (cross-domain için)
    
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=max_age,
        path="/",
        domain=cookie_domain  # None = cross-domain çalışır
    )


def _clear_cookie(response: Response, key: str):
    if COOKIE_DOMAIN:
        response.delete_cookie(key, path="/", domain=COOKIE_DOMAIN)
    else:
        response.delete_cookie(key, path="/")


def _extract_token_from_request(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if auth_header:
        scheme, _, param = auth_header.partition(" ")
        if scheme.lower() == "bearer" and param:
            return param.strip()
    cookie_token = request.cookies.get(ACCESS_TOKEN_COOKIE)
    if cookie_token:
        return cookie_token
    return ""


async def _is_token_blacklisted(jti: str) -> bool:
    if not jti:
        return False
    redis_conn = _get_redis_connection()
    return bool(await redis_conn.get(f"blacklist:{jti}"))


async def _blacklist_token(jti: str, exp: int):
    if not jti or not exp:
        return
    ttl = int(exp - time.time())
    if ttl <= 0:
        return
    redis_conn = _get_redis_connection()
    await redis_conn.setex(f"blacklist:{jti}", ttl, "true")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = _extract_token_from_request(request)
        if not token:
            raise credentials_exception
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_type = payload.get("type", "access")
        if token_type != "access":
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        jti: str = payload.get("jti")
        if await _is_token_blacklisted(jti):
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/logout")
async def logout(request: Request, response: Response):
    tokens_to_revoke = []
    raw_access_token = _extract_token_from_request(request)
    if raw_access_token:
        try:
            tokens_to_revoke.append(
                jwt.decode(raw_access_token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
            )
        except JWTError:
            pass
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE)
    if refresh_token:
        try:
            tokens_to_revoke.append(
                jwt.decode(refresh_token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
            )
        except JWTError:
            pass
    for payload in tokens_to_revoke:
        await _blacklist_token(payload.get("jti"), payload.get("exp"))
    _clear_cookie(response, ACCESS_TOKEN_COOKIE)
    _clear_cookie(response, REFRESH_TOKEN_COOKIE)
    return {"message": "Başarıyla çıkış yapıldı"}

@router.post(
    "/register",
    response_model=schemas.RegisterResponse,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))]
)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Güvenli kayıt endpoint'i - User Enumeration Attack'e karşı korumalı.
    Email zaten kayıtlı olsa bile aynı generic mesajı döner.
    """
    # Normalize email
    normalized_email = user.email.strip().lower()
    
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == normalized_email).first()
    
    if not db_user:
        # Email yeni ise kaydı oluştur
        hashed_password = security.get_password_hash(user.password)
        db_user = models.User(
            email=normalized_email,
            full_name=user.full_name.strip(),
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
    
    # Her iki durumda da aynı generic mesaj döner
    # Böylece saldırgan hangi emailin kayıtlı olduğunu öğrenemez
    return {
        "message": "Kayıt işleminiz alındı. E-posta adresinizi kontrol ediniz.",
        "success": True
    }

@router.post(
    "/token",
    response_model=schemas.AuthResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    normalized_email = form_data.username.strip().lower()
    user = db.query(models.User).filter(models.User.email == normalized_email).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    access_token = security.create_access_token(
        data={"sub": user.email, "type": "access"}, expires_delta=access_token_expires
    )
    refresh_token = security.create_access_token(
        data={"sub": user.email, "type": "refresh"}, expires_delta=refresh_token_expires
    )
    _set_cookie(response, ACCESS_TOKEN_COOKIE, access_token, ACCESS_TOKEN_MAX_AGE)
    _set_cookie(response, REFRESH_TOKEN_COOKIE, refresh_token, REFRESH_TOKEN_MAX_AGE)
    return {
        "message": "Giriş başarılı",
        "token_type": "bearer",
        "access_token": access_token,  # Frontend localStorage için
        "refresh_token": refresh_token,  # Frontend localStorage için
        "expires_in": ACCESS_TOKEN_MAX_AGE,
        "refresh_expires_in": REFRESH_TOKEN_MAX_AGE
    }

@router.post(
    "/refresh",
    response_model=schemas.AuthResponse,
    dependencies=[Depends(RateLimiter(times=30, seconds=60))]
)
async def refresh_access_token(request: Request, response: Response, db: Session = Depends(get_db)):
    # Önce Authorization header'dan token al (cross-domain için)
    refresh_token = _extract_token_from_request(request)
    # Eğer header'da yoksa cookie'den al
    if not refresh_token:
        refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")
    try:
        payload = jwt.decode(refresh_token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        jti = payload.get("jti")
        if await _is_token_blacklisted(jti):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        await _blacklist_token(jti, payload.get("exp"))
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    new_access_token = security.create_access_token(
        data={"sub": user.email, "type": "access"}, expires_delta=access_token_expires
    )
    new_refresh_token = security.create_access_token(
        data={"sub": user.email, "type": "refresh"}, expires_delta=refresh_token_expires
    )
    _set_cookie(response, ACCESS_TOKEN_COOKIE, new_access_token, ACCESS_TOKEN_MAX_AGE)
    _set_cookie(response, REFRESH_TOKEN_COOKIE, new_refresh_token, REFRESH_TOKEN_MAX_AGE)
    return {
        "message": "Token yenilendi",
        "token_type": "bearer",
        "access_token": new_access_token,  # Frontend localStorage için
        "refresh_token": new_refresh_token,  # Frontend localStorage için
        "expires_in": ACCESS_TOKEN_MAX_AGE,
        "refresh_expires_in": REFRESH_TOKEN_MAX_AGE
    }

@router.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Kullanıcı bilgilerini döndürür.
    PERFORMANS: get_current_user zaten kullanıcıyı veritabanından çekiyor,
    bu endpoint sadece mevcut kullanıcıyı döndürür (ek sorgu yok).
    """
    return current_user

