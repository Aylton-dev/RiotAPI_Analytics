from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from src.repository.database import getDb, engine
from src.model import models
from src.scripts import get_match_data

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Riot API Analytics")

@app.get("/")
def status():
    return {"status": "API is running", "project": "Riot API Analytics"}

@app.get("/analytics/winrate")
def get_item_winrate(db: Session = Depends(getDb)):

    return {"message": "Rota de analytics que será implementada futuramente"}