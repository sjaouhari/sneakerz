from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
def root():
    return {"message": "Sneakerz API is running 🚀"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/sneakers")
def get_sneakers():
    return {"sneakers": []}

@app.get("/margins")
def get_margins():
    return {"margins": []}

@app.get("/stats")
def get_stats():
    return {"stats": {}}