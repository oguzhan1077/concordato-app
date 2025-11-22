from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import JWTError, jwt
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
import os
from . import models, schemas, security, database

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        jti: str = payload.get("jti")
        
        if email is None:
            raise credentials_exception
            
        # Redis'ten blacklist kontrolü
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        redis_conn = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        
        if jti:
            is_blacklisted = await redis_conn.get(f"blacklist:{jti}")
            if is_blacklisted:
                raise credentials_exception
        
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        if jti and exp:
            # Redis bağlantısı
            redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
            redis_conn = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
            
            # Kalan süreyi hesapla (saniye cinsinden)
            # Redis'e jti'yi kaydet (expire süresi token'ın kalan ömrü kadar)
            # exp bir timestamp, şimdiki zamanı çıkararak TTL buluyoruz
            import time
            ttl = int(exp - time.time())
            
            if ttl > 0:
                await redis_conn.setex(f"blacklist:{jti}", ttl, "true")
                
        return {"message": "Başarıyla çıkış yapıldı"}
    except JWTError:
        # Token zaten geçersizse işlem yapmaya gerek yok
        return {"message": "Token geçersiz"}

@router.post(
    "/register",
    response_model=schemas.User,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))]
)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post(
    "/token",
    response_model=schemas.Token,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    normalized_email = form_data.username.strip().lower()
    user = db.query(models.User).filter(models.User.email == normalized_email).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

