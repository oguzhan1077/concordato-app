from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import List, Optional
from datetime import datetime
import re
from . import privacy_utils

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
    
    @model_validator(mode='after')
    def mask_personal_data(self):
        """
        KVKK ve TCK 136 uyarınca kişisel verileri maskeler.
        API response'larında otomatik olarak çalışır.
        """
        if privacy_utils.should_mask_data():
            # TC/VKN maskeleme (kısmi - ilk 3 ve son 4 hane görünür)
            if self.tc_vkn:
                self.tc_vkn = privacy_utils.mask_tc_vkn(self.tc_vkn, mask_level="partial")
            
            # Adres maskeleme (sadece şehir görünür)
            if self.adres:
                self.adres = privacy_utils.mask_address(self.adres, show_city=True)
            
            # Karar özeti içindeki kişisel verileri maskele
            if self.karar_ozeti:
                self.karar_ozeti = privacy_utils.mask_text_personal_data(self.karar_ozeti)
        
        return self

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
    
    @model_validator(mode='after')
    def mask_personal_data_in_text(self):
        """
        KVKK ve TCK 136 uyarınca ilan metnindeki kişisel verileri maskeler.
        TC Kimlik No, telefon, email gibi verileri otomatik tespit eder ve maskeler.
        """
        if privacy_utils.should_mask_data():
            # İlan metnindeki kişisel verileri maskele
            if self.metin:
                self.metin = privacy_utils.mask_text_personal_data(
                    self.metin, 
                    aggressive=True  # 11 haneli tüm sayıları maskele
                )
        
        return self

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

class RegisterResponse(BaseModel):
    """
    Güvenli kayıt response'u - User Enumeration Attack'i önlemek için
    email'in kayıtlı olup olmadığını açığa vermez.
    """
    message: str
    success: bool

class AuthResponse(BaseModel):
    """
    Kimlik doğrulama response'u - Token bilgilerini HttpOnly cookie üzerinden gönderir.
    """
    message: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Hata Raporu Schemas ---
class HataRaporuCreate(BaseModel):
    ilan_id: int = Field(..., gt=0, description="İlan ID'si")
    kategori: str = Field(..., description="Hata kategorisi")
    aciklama: str = Field(..., min_length=10, max_length=1000, description="Hata açıklaması")
    
    @field_validator("kategori")
    @classmethod
    def validate_kategori(cls, value: str) -> str:
        valid_categories = ["yanlis_bilgi", "eksik_bilgi", "kvkk_ihlali", "diger"]
        if value not in valid_categories:
            raise ValueError(f"Geçersiz kategori. İzin verilen değerler: {', '.join(valid_categories)}")
        return value
    
    @field_validator("aciklama")
    @classmethod
    def validate_aciklama(cls, value: str) -> str:
        stripped = value.strip()
        if len(stripped) < 10:
            raise ValueError("Açıklama en az 10 karakter olmalıdır")
        return stripped

class HataRaporu(BaseModel):
    id: int
    ilan_id: int
    user_id: int
    kategori: str
    aciklama: str
    durum: str
    olusturma_tarihi: datetime
    guncellenme_tarihi: datetime
    user: Optional[User] = None
    
    class Config:
        from_attributes = True

class HataRaporuResponse(BaseModel):
    message: str
    rapor_id: int
