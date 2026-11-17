import os
import json
from pathlib import Path
import httpx
from dotenv import load_dotenv
import asyncio

load_dotenv() 

RIOT_API_KEY = os.getenv("RIOT_API_KEY")

print("consegue encontrar a riotAPI {RIOT_API_KEY}")

HEADERS = {
    "X-Riot-Token": RIOT_API_KEY
}

KINDRED_CHAMPION_ID = 203

def load_rune_map() -> tuple[dict[int,str], dict[str,str]]:
    path = Path("data/runesReforged.json")

    if not path.exists():
        print(f"Arquivo {path} não encontrado.")
        return {}
    
    with open(path, "r", encoding="utf-8") as file:
        runes_data = json.load(file)
    
    rune_name_map = {}
    style_name_map = {}

    for tree in runes_data:
        tree_id = tree.get("id")
        tree_name = tree.get("name")
        style_name_map[str(tree_id)] = tree_name

        for slot in tree.get("slots", []):
            for rune in slot.get("runes", []):
                rune_id = rune.get("id")
                rune_name = rune.get("name")
                rune_name_map[int(rune_id)] = rune_name

    return rune_name_map, style_name_map
    
def load_item_map() -> dict[int, str]:
    
    file_path = Path("data/item.json")

    with open(file_path, "r", encoding="utf-8") as file:
        items_data = json.load(file)["data"]
    
    item_map = {}
    for item_id_str, details in items_data.items():
        item_map[int(item_id_str)] = details["name"]

    return item_map

async def get_match_data(match_id: str, item_map: dict[int, str], rune_map: dict, style_map: dict):

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

            extracted_runes = []
            perks_data = kindred_player.get("perks", {})
            styles = perks_data.get("styles", [])
            stat_perks = perks_data.get("statPerks", {})

            for style_obj in styles:
                description = style_obj.get("description")
                raw_style_id = style_obj.get("style")

                style_name = style_map.get(str(raw_style_id), str(raw_style_id))

                selections = style_obj.get("selections", [])

                for index, selection in enumerate(selections):
                    rune_id = selection.get("perk")

                    perk_name = rune_map.get(rune_id, f"Desconhecido({rune_id})")

                    category = "keystone" if(description == "primaryStyle" and index == 0) else ("primary_runes" if description == "primaryStyle" else "secondary_runes")

                    extracted_runes.append({
                        "perk_name": perk_name, 
                        "category": category,
                        "style_id": style_name
                    })

            for stat_type in ["offense", "flex", "defense"]:
                if stat_type in stat_perks:
                    stat_id = stat_perks[stat_type]
                    extracted_runes.append({
                        "perk_name": f"StatShard({stat_id})",
                        "category": "stat_shard",
                        "style_id": "StatShards"
                    })          

            return {
                "match_id": match_id,
                "duration": duration,
                "kindred_win": kindred_player["win"],
                "kindred_items": translated_items,
                "kindred_runes": extracted_runes,
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
