from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://sneakerz_user:sneakerz123@localhost:5432/sneakerz"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ── Models ────────────────────────────────────────────────────
class Sneaker(Base):
    __tablename__ = "sneakers"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    brand         = Column(String)
    price_retail  = Column(Float)
    currency      = Column(String, default="EUR")
    source        = Column(String)
    url           = Column(String)
    image         = Column(String)
    layer         = Column(String, default="bronze")
    ingested_at   = Column(DateTime, default=datetime.now)

class Margin(Base):
    __tablename__ = "margins"

    id                = Column(Integer, primary_key=True, index=True)
    sneaker_name      = Column(String)
    brand             = Column(String)
    price_retail      = Column(Float)
    price_resell      = Column(Float)
    margin_value      = Column(Float)
    margin_percent    = Column(Float)
    resell_score      = Column(Integer)  # 0-100 notre feature unique !
    source_retail     = Column(String)
    calculated_at     = Column(DateTime, default=datetime.now)

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées !")

if __name__ == "__main__":
    create_tables()