import os
import json
from pathlib import Path
import httpx
from dotenv import load_dotenv
import asyncio

load_dotenv() 

RIOT_API_KEY = os.getenv("RIOT_API_KEY")

HEADERS = {
    "X-Riot-Token": RIOT_API_KEY
}

KINDRED_CHAMPION_ID = 203

def load_item_map() -> dict[int, str]:
    
    file_path = Path("data/item.json")

    with open(file_path, "r", encoding="utf-8") as file:
        items_data = json.load(file)["data"]
    
    item_map = {}
    for item_id_str, details in items_data.items():
        item_map[int(item_id_str)] = details["name"]

    return item_map

async def get_match_data(match_id: str, item_map: dict[int, str]):

    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
    await asyncio.sleep(0.2)

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
            raw_items = [
                kindred_player["item0"], kindred_player["item1"], kindred_player["item2"],
                kindred_player["item3"], kindred_player["item4"], kindred_player["item5"]
            ]

            translated_items = [
                item_map.get(item_id, f"Desconhecido({item_id})")
                for item_id in raw_items if item_id != 0
            ]

            return {
                "match_id": match_id,
                "duration": duration,
                "kindred_win": kindred_player["win"],
                "kindred_items": translated_items,
                "enemy_jungle_player": enemy_jungle_player
            }
        
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
