import getpass
import sys
import os

# Add the current directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
from app.security import get_password_hash

def create_superuser():
    print("Superuser oluşturma sihirbazına hoş geldiniz.")
    
    email = input("E-posta adresi: ").strip()
    if not email:
        print("Hata: E-posta adresi boş olamaz.")
        return

    # Check if user already exists
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"Hata: '{email}' adresiyle kayıtlı bir kullanıcı zaten var.")
            return
        
        full_name = input("Ad Soyad: ").strip()
        if not full_name:
            print("Hata: Ad Soyad boş olamaz.")
            return

        password = getpass.getpass("Şifre: ")
        password_confirm = getpass.getpass("Şifre (Tekrar): ")

        if password != password_confirm:
            print("Hata: Şifreler eşleşmiyor.")
            return
        
        if len(password) < 6:
             print("Hata: Şifre en az 6 karakter olmalıdır.")
             return

        hashed_password = get_password_hash(password)
        
        new_superuser = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=True
        )

        db.add(new_superuser)
        db.commit()
        db.refresh(new_superuser)
        
        print(f"Başarılı: Superuser '{email}' oluşturuldu (ID: {new_superuser.id}).")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_superuser()

