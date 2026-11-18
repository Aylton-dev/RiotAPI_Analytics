import json 
import os
from pathlib import Path
import pandas as pd
from src.repository.database import engine

def get_valid_items_names(min_gold=2000):
    path = Path("data/item.json")

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    valid_items= []
    for item_id, item_info in data.get("data", {}).items():
        gold_total = item_info["gold"].get("total", 0)

        if gold_total >= min_gold:
            valid_items.append(item_info.get("name"))

    return valid_items

def analyze_item_winrate():

    query = """
        SELECT 
            m.match_id,
            m.duration,
            m.kindred_winner,
            i.item_name,
            i.buy_order
        FROM matches m
        JOIN item_partida i ON m.match_id = i.match_id
    """

    df = pd.read_sql(query, con=engine)

    if df.empty:
        print("Nenhum dado encontrado para análise.")
        return []

    itens_validos = get_valid_items_names(min_gold=2000)

    if itens_validos:
        df = df[df['item_name'].isin(itens_validos)]

    if df.empty:
        return []

    item_stats = df.groupby(['buy_order', 'item_name']).agg(
        total_matches=("match_id", "nunique"),
        wins=("kindred_winner", "sum")
    ).reset_index()

    item_stats['win_rate'] = (item_stats['wins'] / item_stats['total_matches']) * 100
    item_stats['win_rate'] = item_stats['win_rate'].round(2)

    item_stats = item_stats.sort_values(by=['buy_order', 'total_matches'], ascending=[True, False])

    item_stats["buy_order"] = item_stats["buy_order"].astype(int)
    item_stats["total_matches"] = item_stats["total_matches"].astype(int)
    item_stats["wins"] = item_stats["wins"].astype(int)
    item_stats["win_rate"] = item_stats["win_rate"].astype(float)

    return item_stats.to_dict(orient="records")

def analyze_perk_winrate():

    query = """
        SELECT
            m.match_id,
            m.kindred_winner,
            r.perk_name,
            r.category,
            r.style_id
        FROM matches m
        JOIN runa_partida r ON m.match_id = r.match_id
    """

    df = pd.read_sql(query, con=engine)

    if df.empty:
        print("Nenhum dado encontrado para análise.")
        return []

    if 'category' in df.columns:
        df = df[df['category'] != 'stat_shard']

    rune_stats = df.groupby(['perk_name', 'category', 'style_id']).agg(
        total_matches=("match_id", "nunique"),
        wins=("kindred_winner", "sum")
    ).reset_index()

    rune_stats['win_rate'] = (rune_stats['wins'] / rune_stats['total_matches']) * 100
    rune_stats['win_rate'] = rune_stats['win_rate'].round(2)

    def get_perk_priority(category):
        cat = str(category).lower()
        if 'keystone' in cat or 'pilar' in cat:
            return 1
        elif 'primary' in cat or 'principal' in cat:
            return 2
        elif 'secondary' in cat or 'secundaria' in cat:
            return 3
        return 4

    rune_stats['priority'] = rune_stats['category'].apply(get_perk_priority)

    rune_stats = rune_stats.sort_values(by=['priority', 'total_matches'], ascending=[True, False])

    rune_stats = rune_stats.drop(columns=['priority'])

    rune_stats["total_matches"] = rune_stats["total_matches"].astype(int)
    rune_stats["wins"] = rune_stats["wins"].astype(int)
    rune_stats["win_rate"] = rune_stats["win_rate"].astype(float)

    return rune_stats.to_dict(orient="records")
    
def analyze_matchup_winrate():

    query = """
        SELECT
            match_id,
            kindred_winner,
            enemy_jungler
        FROM matches
        WHERE enemy_jungler IS NOT NULL
    """

    df = pd.read_sql(query, con=engine)

    if df.empty:
        print("Nenhum dado encontrado para análise.")
        return []
    
    matchup_stats = df.groupby('enemy_jungler').agg(
        total_matches=("match_id", "nunique"),
        wins=("kindred_winner", sum)
    ).reset_index()

    matchup_stats['win_rate'] = (matchup_stats['wins'] / matchup_stats['total_matches']) * 100
    matchup_stats['win_rate'] = matchup_stats['win_rate'].round(2)

    matchup_stats = matchup_stats.sort_values(by='total_matches', ascending=False)

    matchup_stats["total_matches"] = matchup_stats["total_matches"].astype(int)
    matchup_stats["wins"] = matchup_stats["wins"].astype(int)
    matchup_stats["win_rate"] = matchup_stats["win_rate"].astype(float)

    return matchup_stats.to_dict(orient="records")