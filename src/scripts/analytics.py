import asyncio
import os
from src.scripts.riotApi import get_match_ids_by_puuid, get_match_data, load_item_map, load_rune_map
from src.repository.database import SessionLocal, engine
from src.repository.crud import save_matches
from src.model import models
from dotenv import load_dotenv

models.Base.metadata.create_all(bind=engine)
load_dotenv()

async def match_farmer(puuid:str):

    item_map = load_item_map()
    rune_map, style_map = load_rune_map()

    matches_ids = await get_match_ids_by_puuid(puuid, count=50)

    if not matches_ids:
        print(f"Não foi possível obter partidas para o PUUID {puuid}.")
        return []

    semaforo = asyncio.Semaphore(5)

    async def fetch_with_semaphore(match_id: str):
        async with semaforo:
            return await get_match_data(match_id, item_map, rune_map, style_map)

    tasks = [fetch_with_semaphore(match_id) for match_id in matches_ids]

    results = await asyncio.gather(*tasks)

    matches_filtered = [p for p in results if p is not None]

    if matches_filtered:
        db = SessionLocal()
        try:
            save_matches(db, matches_filtered)
        finally:
            db.close()
    else:
        print("Nenhuma partida válida de Kindred encontrada neste lote.")

if __name__ == "__main__":
    PUUID = os.getenv("RIOT_PUUID")

    if not PUUID:
        raise SystemExit(
            "RIOT_PUUID nao configurado. Defina RIOT_PUUID no arquivo .env."
        )
    
    print("Iniciando o teste de captura de dados...")
    dados_finais = asyncio.run(match_farmer(PUUID))
    print(dados_finais)