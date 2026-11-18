from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from src.repository.database import getDb, engine
from src.model import models
from src.scripts.riotApi import get_match_data
from src.repository.analyzeWinrate import analyze_item_winrate, analyze_perk_winrate, analyze_matchup_winrate

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Riot API Analytics")

@app.get("/")
def status():
    return {"status": "API is running", "project": "Riot API Analytics"}

@app.get("/analytics/winrate/items")
def get_item_winrate(db: Session = Depends(getDb)):

    return analyze_item_winrate()

@app.get("/analytics/winrate/perks")
def get_perk_winrate(db: Session = Depends(getDb)):

    return analyze_perk_winrate()

@app.get("/analytics/winrate/matchups")
def get_matchups_winrate(db: Session = Depends(getDb)):

    return analyze_matchup_winrate()