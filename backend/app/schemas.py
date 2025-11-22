from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

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
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

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
