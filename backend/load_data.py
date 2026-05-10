import json
import os
import glob
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://sneakerz_user:sneakerz123@localhost:5432/sneakerz"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ── Models ─────────────────────────────────────────────────────
class Sneaker(Base):
    __tablename__ = "sneakers"
    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String)
    brand        = Column(String)
    price_retail = Column(Float)
    currency     = Column(String)
    source       = Column(String)
    url          = Column(String)
    image        = Column(String)
    layer        = Column(String, default="silver")
    ingested_at  = Column(DateTime, default=datetime.now)

class Margin(Base):
    __tablename__ = "margins"
    id             = Column(Integer, primary_key=True, index=True)
    sneaker_name   = Column(String)
    brand          = Column(String)
    price_retail   = Column(Float)
    price_resell   = Column(Float)
    margin_value   = Column(Float)
    margin_percent = Column(Float)
    resell_score   = Column(Integer)
    source_retail  = Column(String)
    calculated_at  = Column(DateTime, default=datetime.now)

def compute_resell_score(margin_percent, brand):
    """Score unique 0-100 basé sur marge + popularité marque"""
    brand_bonus = {
        'Jordan': 20, 'Nike': 15, 'Adidas': 12,
        'New Balance': 10, 'Asics': 8, 'Salomon': 8,
        'Puma': 6, 'Converse': 5, 'Unknown': 0
    }
    # Score basé sur la marge (max 80 points)
    margin_score = min(80, (margin_percent / 200) * 80)
    # Bonus marque (max 20 points)
    bonus = brand_bonus.get(brand, 5)
    return min(100, int(margin_score + bonus))

def load_silver_to_postgres():
    """Charge les données Silver dans la table sneakers"""
    print("=== Chargement Silver → PostgreSQL ===")

    silver_dir = '../scraper/data/silver'
    files = glob.glob(f"{silver_dir}/*.json")

    if not files:
        print("❌ Aucun fichier Silver trouvé !")
        return

    db = SessionLocal()

    # Vider la table avant de recharger
    db.query(Sneaker).delete()
    db.commit()

    total = 0
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            items = json.load(f)

        for item in items:
            sneaker = Sneaker(
                name         = item.get('name', ''),
                brand        = item.get('brand', 'Unknown'),
                price_retail = item.get('price_retail', 0),
                currency     = item.get('currency', 'EUR'),
                source       = item.get('source', ''),
                url          = item.get('url', ''),
                image        = item.get('image', ''),
                layer        = 'silver',
                ingested_at  = datetime.now()
            )
            db.add(sneaker)
            total += 1

    db.commit()
    db.close()
    print(f"✅ {total} sneakers chargés dans PostgreSQL !")

def load_gold_to_postgres():
    """Charge les données Gold dans la table margins"""
    print("=== Chargement Gold → PostgreSQL ===")

    gold_dir = '../scraper/data/gold'
    files = glob.glob(f"{gold_dir}/*.json")

    if not files:
        print("❌ Aucun fichier Gold trouvé !")
        return

    # Prendre le fichier le plus récent
    latest = max(files, key=os.path.getctime)

    with open(latest, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)

    margins = gold_data.get('all_margins', [])

    db = SessionLocal()

    # Vider la table avant de recharger
    db.query(Margin).delete()
    db.commit()

    total = 0
    for m in margins:
        score = compute_resell_score(
            m.get('margin_percent', 0),
            m.get('brand', 'Unknown')
        )
        margin = Margin(
            sneaker_name   = m.get('name', ''),
            brand          = m.get('brand', 'Unknown'),
            price_retail   = m.get('price_retail', 0),
            price_resell   = m.get('price_resell_ebay', 0),
            margin_value   = m.get('margin_value', 0),
            margin_percent = m.get('margin_percent', 0),
            resell_score   = score,
            source_retail  = m.get('source_retail', ''),
            calculated_at  = datetime.now()
        )
        db.add(margin)
        total += 1

    db.commit()
    db.close()
    print(f"✅ {total} marges chargées dans PostgreSQL !")
    print(f"📁 Fichier source : {latest}")

if __name__ == "__main__":
    print("🚀 Initialisation PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées !")
    load_silver_to_postgres()
    load_gold_to_postgres()
    print("\n✅ PostgreSQL prêt !")