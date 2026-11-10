import os
import httpx
from dotenv import load_dotenv

load_dotenv() 

RIOT_API_KEY = os.getenv("RIOT_API_KEY")

HEADERS = {
    "X-Riot-Token": RIOT_API_KEY
}

KINDRED_CHAMPION_ID = 203

async def get_match_data(match_id: str):

    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"Erro ao buscar partida {match_id}: Status {response.status_code}")
            return None
        
        match_json = response.json()
        duration = match_json["info"]["gameDuration"]

        if duration < 240:
            print("partida descartada por ser muito curta")
            return None

        participants = match_json["info"]["participants"]

        kindred_player = None
        enemy_jungle_player = None

        for participant in participants:
            if participant["individualPosition"] == "JUNGLE":
                if participant["championId"] == KINDRED_CHAMPION_ID:
                    kindred_player = participant
                else:
                    enemy_jungle_player = participant["championName"]
        if kindred_player is not None:
            matches_data = {
                "match_id": match_id,
                "duration": duration,
                "kindred_win": kindred_player["win"],
                "kindred_items": [
                kindred_player["item0"], kindred_player["item1"], kindred_player["item2"],
                kindred_player["item3"], kindred_player["item4"], kindred_player["item5"]
            ],
                "enemy_jungle_champion": enemy_jungle_player
            }
            return matches_data

        return None

async def get_match_ids_by_puuid(puuid: str, count: int = 20) -> list[str]:

    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"

    params = {
        "queueId": 420,
        "count": count
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS, params=params)

        if response.status_code != 200:
            print(f"Erro ao buscar partidas para o PUUID {puuid}: Status {response.status_code}")
            return []

        match_ids = response.json()

        print(f"Sucesso! Encontrados {len(match_ids)} Match IDs para o jogador.")
        return match_ids
