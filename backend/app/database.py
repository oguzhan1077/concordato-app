from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Railway MYSQL_URL kullan (eğer varsa) - Railway template variable
MYSQL_URL = os.getenv("MYSQL_URL")

if MYSQL_URL:
    # Railway'den gelen tam URL kullan
    # Format: mysql://user:password@host:port/database
    # SQLAlchemy için mysql+mysqlconnector:// prefix'i ekle
    SQLALCHEMY_DATABASE_URL = MYSQL_URL.replace("mysql://", "mysql+mysqlconnector://")
else:
    # Fallback: Ayrı değişkenler kullan (Docker/local için)
    DB_HOST = os.getenv("DB_HOST", "db")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "ilan_db")
    
    if DB_PASSWORD:
        SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    else:
        SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}@{DB_HOST}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

