from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from load_data import SessionLocal, Sneaker, Margin, Base, engine

app = FastAPI(
    title="Sneakerz API",
    description="Plateforme Big Data d'analyse du marché sneakers",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Créer les tables au démarrage
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Sneakerz API is running 🚀"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/sneakers")
def get_sneakers(db: Session = Depends(get_db)):
    sneakers = db.query(Sneaker).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "brand": s.brand,
            "price_retail": s.price_retail,
            "currency": s.currency,
            "source": s.source,
            "url": s.url,
        }
        for s in sneakers
    ]

@app.get("/api/margins")
def get_margins(db: Session = Depends(get_db)):
    margins = db.query(Margin).order_by(
        Margin.margin_value.desc()
    ).all()
    return [
        {
            "sneaker_name": m.sneaker_name,
            "brand": m.brand,
            "price_retail": m.price_retail,
            "price_resell": m.price_resell,
            "margin_value": m.margin_value,
            "margin_percent": m.margin_percent,
            "resell_score": m.resell_score,
        }
        for m in margins
    ]

@app.get("/api/margins/top/{n}")
def get_top_margins(n: int, db: Session = Depends(get_db)):
    margins = db.query(Margin).order_by(
        Margin.margin_value.desc()
    ).limit(n).all()
    return [
        {
            "sneaker_name": m.sneaker_name,
            "brand": m.brand,
            "margin_value": m.margin_value,
            "margin_percent": m.margin_percent,
            "resell_score": m.resell_score,
        }
        for m in margins
    ]

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func

    total_sneakers = db.query(Sneaker).count()
    total_margins  = db.query(Margin).count()
    avg_margin     = db.query(
        func.avg(Margin.margin_percent)
    ).scalar() or 0
    best = db.query(Margin).order_by(
        Margin.margin_value.desc()
    ).first()

    return {
        "total_sneakers": total_sneakers,
        "total_margins": total_margins,
        "avg_margin_percent": round(avg_margin, 1),
        "best_opportunity": {
            "name": best.sneaker_name if best else None,
            "margin": best.margin_value if best else 0,
            "margin_percent": best.margin_percent if best else 0,
        }
    }

@app.get("/api/brands")
def get_brands(db: Session = Depends(get_db)):
    from sqlalchemy import func
    brands = db.query(
        Sneaker.brand,
        func.count(Sneaker.id).label("count")
    ).group_by(Sneaker.brand).all()
    return [{"brand": b, "count": c} for b, c in brands]