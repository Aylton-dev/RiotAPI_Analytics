import asyncio
from src.scripts.riotApi import get_match_ids_by_puuid, get_match_data

async def match_farmer(puuid:str):
    matches_ids = await get_match_ids_by_puuid(puuid, count=20)

    if not matches_ids:
        print(f"Não foi possível obter partidas para o PUUID {puuid}.")
        return []

    tasks = [get_match_data(match_id) for match_id in matches_ids]

    results = await asyncio.gather(*tasks)

    matches_filtered = [p for p in results if p is not None]

    print(f"Processamento concluído. {len(matches_filtered)} partidas estruturadas com sucesso!")
    return matches_filtered 

if __name__ == "__main__":
    
    TEST_PUUID = "xQSyfeLVGfQiLbLQNc8ygiTpLLYLjpxWq6vEC_H2j2mDY52bkip55Go83nSUjmK0VHM9eDBastpa2w"
    
    print("Iniciando o teste de captura de dados...")
    dados_finais = asyncio.run(match_farmer(TEST_PUUID))
    print(dados_finais)