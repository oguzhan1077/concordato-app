from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime
import re

# --- Borçlu Schemas ---
class IlanBorcluBase(BaseModel):
    borclu_adi: Optional[str] = None
    borclu_tipi: Optional[str] = None
    tc_vkn: Optional[str] = None
    ticaret_sicil_no: Optional[str] = None
    adres: Optional[str] = None
    karar_turu: Optional[str] = None
    karar_ozeti: Optional[str] = None
    karar_tarihi: Optional[str] = None
    karar_baslangic_tarihi: Optional[str] = None
    muhlet_suresi: Optional[str] = None
    mahkeme_adi: Optional[str] = None
    dosya_esas_no: Optional[str] = None
    komiserler: Optional[str] = None
    durusma_tarihi: Optional[str] = None

class IlanBorcluCreate(IlanBorcluBase):
    pass

class IlanBorclu(IlanBorcluBase):
    id: int
    ilan_id: int
    analiz_tarihi: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- İlan Schemas ---
class IlanBase(BaseModel):
    ilan_no: str
    baslik: Optional[str] = None
    sehir: Optional[str] = None
    ilce: Optional[str] = None
    kurum: Optional[str] = None
    ilan_turu: Optional[str] = None
    metin: Optional[str] = None
    link: Optional[str] = None
    yayin_tarihi: Optional[str] = None

class IlanCreate(IlanBase):
    pass

class Ilan(IlanBase):
    id: int
    eklenme_tarihi: Optional[datetime] = None
    borclular: List[IlanBorclu] = []

    class Config:
        from_attributes = True

class Stats(BaseModel):
    total_ilan: int
    top_cities: List[dict]
    last_update: str

# --- User Schemas ---
NAME_REGEX = re.compile(r"^[A-Za-zÇĞİÖŞÜçğöşıü0-9\s\.'-]{2,100}$")
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,128}$")

class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=254)
    full_name: str = Field(..., min_length=2, max_length=100)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        normalized = value.strip()
        if not NAME_REGEX.match(normalized):
            raise ValueError("Ad alanı harf, rakam, boşluk ve .'- karakterlerini içerebilir")
        return normalized

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if len(normalized) > 254:
            raise ValueError("E-posta 254 karakteri aşamaz")
        return normalized

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not PASSWORD_REGEX.match(value):
            raise ValueError("Şifre en az bir büyük, bir küçük harf, bir rakam ve özel karakter içermelidir")
        return value

class UserLogin(BaseModel):
    email: EmailStr = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_login_email(cls, value: str) -> str:
        return value.strip().lower()

class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
