from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from src.repository.database import getDb, engine
from src.model import models
from src.scripts.riotApi import get_match_data
from src.repository.analyzeItems import analyze_item_winrate

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Riot API Analytics")

@app.get("/")
def status():
    return {"status": "API is running", "project": "Riot API Analytics"}

@app.get("/analytics/winrate")
def get_item_winrate(db: Session = Depends(getDb)):

    return analyze_item_winrate()