from sqlalchemy.orm import Session
from src.model.models import Match, ItemPartida

def save_matches(db: Session, matches_list: list[dict]):
    new_matches = 0

    for match_data in matches_list:
        
        existing_match = db.query(Match).filter(Match.match_id == match_data["match_id"]).first()
        if existing_match:
            continue

        new_match = Match(
            match_id=match_data["match_id"],
            duration=match_data["duration"],
            kindred_winner=match_data["kindred_win"],
            enemy_jungler=match_data["enemy_jungle_player"]
        )
        db.add(new_match)

        
        for index, item_name in enumerate(match_data["kindred_items"], start=1):
            new_item = ItemPartida(
                match_id=match_data["match_id"],
                item_name=item_name,
                buy_order=index
            )
            db.add(new_item)

        new_matches += 1
    
    db.commit()
    print(f"Sucesso! {new_matches} novas partidas foram salvas no banco de dados.")