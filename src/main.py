from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.repository.database import getDb, engine
from src.model import models
from src.scripts.riotApi import get_match_data
from src.repository.analyzeWinrate import analyze_item_winrate, analyze_perk_winrate, analyze_matchup_winrate
from fastapi.staticfiles import StaticFiles
from src.ia.ai_analytic_perks import PerkAnalysisRequest, PerkAnalysisResponse, AIProviderError, InvalidPerkError, PerkAIService
from src.ia.ai_analytic import AIProviderError, InvalidItemError, ItemAIService, ItemAnalysisRequest, ItemAnalysisResponse, DatasetAnomalyReport
from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Riot API Analytics")
ai_service = ItemAIService()
ai_perk_service = PerkAIService()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/data", StaticFiles(directory="data"), name="data")

print("acesse essa URL: http://127.0.0.1:8000/static/index.html")

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

@app.post("/ai/items/analysis", response_model=ItemAnalysisResponse)
def analyze_item_endpoint(payload: ItemAnalysisRequest) -> ItemAnalysisResponse:
    try:
        return ai_service.analyze_item(payload)
    except InvalidItemError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except AIProviderError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

@app.get("/ai/anomalies", response_model=DatasetAnomalyReport)
def find_anomalies_endpoint() -> DatasetAnomalyReport:
    try:
        return ai_service.find_anomalies_with_ai()
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@app.post("/ai/perks/analysis", response_model=PerkAnalysisResponse)
def analyze_perk_endpoint(payload: PerkAnalysisRequest) -> PerkAnalysisResponse:
    try:
        return ai_perk_service.analyze_perk(payload)
    except InvalidItemError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except AIProviderError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc