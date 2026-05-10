from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import SessionLocal, Sneaker, Margin
import json
import os

router = APIRouter(prefix="/api", tags=["sneakers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/sneakers")
def get_all_sneakers(db: Session = Depends(get_db)):
    sneakers = db.query(Sneaker).all()
    return sneakers

@router.get("/margins")
def get_all_margins(db: Session = Depends(get_db)):
    margins = db.query(Margin).order_by(
        Margin.margin_value.desc()
    ).all()
    return margins

@router.get("/margins/top/{n}")
def get_top_margins(n: int, db: Session = Depends(get_db)):
    margins = db.query(Margin).order_by(
        Margin.margin_value.desc()
    ).limit(n).all()
    return margins

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_sneakers = db.query(Sneaker).count()
    total_margins  = db.query(Margin).count()

    best = db.query(Margin).order_by(
        Margin.margin_value.desc()
    ).first()

    return {
        "total_sneakers": total_sneakers,
        "total_margins": total_margins,
        "best_opportunity": {
            "name": best.sneaker_name if best else None,
            "margin": best.margin_value if best else 0,
            "margin_percent": best.margin_percent if best else 0,
        }
    }

@router.get("/brands")
def get_brands(db: Session = Depends(get_db)):
    from sqlalchemy import func
    brands = db.query(
        Sneaker.brand,
        func.count(Sneaker.id).label("count")
    ).group_by(Sneaker.brand).all()
    return [{"brand": b, "count": c} for b, c in brands]