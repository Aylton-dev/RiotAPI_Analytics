import pandas as pd
from src.repository.database import engine

def analyze_item_winrate():

    query = """
        SELECT 
            m.match_id,
            m.duration,
            m.kindred_winner,
            m.enemy_jungler,
            i.item_name,
            i.buy_order
        FROM matches m
        JOIN item_partida i ON m.match_id = i.match_id
    """

    df = pd.read_sql(query, con=engine)

    if df.empty:
        print("Nenhum dado encontrado para análise.")
        return

    item_stats = df.groupby('item_name').agg(
        total_matches=("match_id", "count"),
        wins=("kindred_winner", "sum")
    ).reset_index()

    item_stats['win_rate'] = (item_stats['wins'] / item_stats['total_matches']) * 100
    item_stats['win_rate'] = item_stats['win_rate'].round(2)

    item_stats = item_stats.sort_values(by='total_matches', ascending=False)

    item_stats["total_matches"] = item_stats["total_matches"].astype(int)
    item_stats["wins"] = item_stats["wins"].astype(int)
    item_stats["win_rate"] = item_stats["win_rate"].astype(float)

    return item_stats.to_dict(orient="records")
