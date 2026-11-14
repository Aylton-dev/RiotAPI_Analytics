# Riot API Analytics

Projeto em Python para coletar partidas ranqueadas de League of Legends pela Riot Games API, armazenar os itens comprados por partidas de Kindred na jungle e disponibilizar uma análise de taxa de vitória por item em uma API REST.

## Como funciona

1. O coletor consulta os IDs das últimas 20 partidas da fila ranqueada solo/duo (`queueId=420`) de um jogador, usando o endpoint de Match-V5 da região `americas`.
2. Busca os detalhes das partidas e mantém apenas partidas com Kindred na jungle e duração de pelo menos 240 segundos.
3. Traduz os IDs dos itens com o catálogo local `data/item.json` e salva a partida e os itens no SQLite. Partidas já cadastradas não são inseridas novamente.
4. A API calcula, para cada item, o total de registros de compra, o número de vitórias de Kindred e a taxa de vitória percentual. Os resultados são ordenados pela quantidade de registros de compra, do maior para o menor.

O nome do projeto é genérico, mas a coleta e as métricas atuais são específicas para Kindred na jungle.

## Requisitos

- Python 3.10 ou superior.
- Uma chave de desenvolvedor da Riot Games API.
- Um PUUID de jogador para executar a coleta.

## Instalação

No PowerShell, na pasta do projeto:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz do projeto:

```dotenv
RIOT_API_KEY=sua_chave_da_riot
# Opcional; este é também o valor padrão:
DATABASE_URL=sqlite:///./RiotAPI_Analytics.db
```

O banco SQLite é criado automaticamente quando a aplicação ou o coletor inicializa os modelos. O caminho padrão é relativo ao diretório em que o comando é executado.

## Executar a API

Com o ambiente virtual ativado:

```powershell
uvicorn src.main:app --reload
```

A API ficará disponível em `http://127.0.0.1:8000`.

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Verifica se a API está ativa. |
| `GET` | `/analytics/winrate` | Retorna as estatísticas de vitória por item com base nos dados salvos. |

A documentação interativa do FastAPI fica em `http://127.0.0.1:8000/docs`.

Exemplo de resposta de `/analytics/winrate`:

```json
[
  {
    "item_name": "Nome do item",
    "total_matches": 10,
    "wins": 6,
    "win_rate": 60.0
  }
]
```

Se ainda não houver dados relacionados entre partidas e itens, a análise atualmente retorna `null`.

## Coletar partidas

O script `src/scripts/analytics.py` executa a coleta de forma assíncrona, com até cinco consultas simultâneas aos detalhes das partidas. Para escolher o jogador, edite a constante `TEST_PUUID` nesse arquivo e substitua-a pelo PUUID desejado. Em seguida, execute na raiz do projeto:

```powershell
python -m src.scripts.analytics
```

É necessária uma chave válida em `RIOT_API_KEY`. A API de coleta usa a rota regional `americas`; partidas que não atendem aos filtros ou que não podem ser consultadas não são armazenadas.

## Estrutura do projeto

```text
.
├── data/
│   └── item.json                 # Catálogo local de itens
├── src/
│   ├── main.py                   # Aplicação FastAPI e rotas
│   ├── model/
│   │   └── models.py             # Modelos SQLAlchemy
│   ├── repository/
│   │   ├── analyzeItems.py       # Consulta e cálculo das métricas
│   │   ├── crud.py               # Persistência de partidas e itens
│   │   └── database.py           # Engine, sessões e configuração do banco
│   └── scripts/
│       ├── analytics.py          # Orquestração da coleta
│       └── riotApi.py            # Chamadas à Riot API e leitura dos itens
├── requirements.txt
└── RiotAPI_Analytics.db          # Banco SQLite local (gerado/atualizado em execução)
```

## Tecnologias

- **FastAPI** e **Uvicorn**: API HTTP.
- **SQLAlchemy**: modelos e acesso ao banco.
- **SQLite**: armazenamento local padrão.
- **Pandas**: agregação das estatísticas por item.
- **HTTPX**: chamadas assíncronas à Riot Games API.
- **python-dotenv**: leitura das configurações do arquivo `.env`.

## Observações

- O arquivo `.env`, ambientes virtuais e arquivos de banco de dados estão excluídos do Git pelo `.gitignore`.
- O coletor usa o catálogo presente em `data/item.json`.
- A taxa de vitória é calculada sobre os registros de item retornados pela junção entre partidas e compras. Cada item de uma partida contribui para a contagem daquele item.
