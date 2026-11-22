from sqlalchemy.orm import Session
from src.model.models import Match, ItemPartida, RunaPartida
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_URL = f"sqlite:///{BASE_DIR / 'RiotAPI_Analytics.db'}"

def save_matches(db: Session, matches_list: list[dict]):

    url = db.get_bind().url
    print(f"Banco em uso: {os.path.abspath(url.database) if url.database else url}")
    print(f"Partidas recebidas para salvar: {len(matches_list)}")
    puladas = 0
    new_matches = 0

    for match_data in matches_list:
        
        existing_match = db.query(Match).filter(Match.match_id == match_data["match_id"]).first()
        if existing_match:
            print(f"{match_data['match_id']} já está no banco, pulando")
            puladas += 1
            continue

        new_match = Match(
            match_id=match_data["match_id"],
            duration=match_data["duration"],
            kindred_winner=match_data["kindred_win"],
            enemy_jungler=match_data["enemy_jungle_player"]
        )
        db.add(new_match)

        
        for index, item_name in enumerate(match_data["kindred_items"], start=1):
            db.add(ItemPartida(match_id=match_data["match_id"], item_name=item_name, buy_order=index))

        for rune_data in match_data.get("kindred_runes", []):
            db.add(RunaPartida(
                match_id=match_data["match_id"],
                perk_name=rune_data["perk_name"],
                category=rune_data["category"],
                style_id=rune_data["style_id"]
            ))

        new_matches += 1
    
    db.commit()
    print(f"Sucesso! {new_matches} novas partidas foram salvas no banco de dados.")