# Riot API Analytics

Aplicação em Python para coletar partidas de **Kindred na Jungle**, armazenar itens, runas e o jungler adversário no SQLite e apresentar estatísticas de winrate em um dashboard web.

O projeto combina a Riot Match-V5 API, Data Dragon, FastAPI, SQLAlchemy, Pandas e o Gemini para disponibilizar métricas agregadas e análises geradas por IA.

## Funcionalidades

- Coleta das últimas partidas ranqueadas solo/duo de um PUUID.
- Filtro das partidas em que Kindred jogou na jungle e que duraram pelo menos 240 segundos.
- Persistência no SQLite com prevenção de partidas duplicadas.
- Análise de winrate por item, considerando a ordem de compra.
- Análise de winrate por runa.
- Análise de winrate contra cada jungler adversário.
- Dashboard web com abas para itens, runas e matchups.
- Análise opcional de itens e runas com IA.
- Detecção opcional de possíveis anomalias no conjunto de dados de itens.

## Como funciona

1. `src/scripts/analytics.py` inicia o coletor com um PUUID informado no código.
2. `src/scripts/riotApi.py` consulta os Match IDs pela Riot Match-V5 API na região `americas`.
3. Somente partidas válidas são processadas:
   - fila ranqueada solo/duo;
   - duração igual ou superior a 240 segundos;
   - Kindred na posição de jungle.
4. Os itens são traduzidos com `data/item.json` e as runas com `data/runesReforged.json`.
5. `src/repository/crud.py` salva as partidas, itens, runas e o nome do campeão do jungler adversário no SQLite.
6. FastAPI expõe métricas agregadas e uma interface estática disponível em `/static/index.html`.

## Tecnologias

- Python 3.10+
- FastAPI e Uvicorn
- SQLAlchemy
- SQLite
- Pandas
- HTTPX
- python-dotenv
- Google Gen AI SDK
- HTML, CSS e JavaScript

## Pré-requisitos

- Python 3.10 ou superior.
- Chave de desenvolvedor da Riot Games API.
- PUUID do jogador usado na coleta.
- Opcional: chave da API Gemini para os endpoints de IA.

## Instalação

Na raiz do projeto:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz:

```dotenv
RIOT_API_KEY=sua_chave_da_riot
GEMINI_API_KEY=sua_chave_gemini
GEMINI_MODEL=gemini-3.5-flash-lite
DATABASE_URL=sqlite:///./RiotAPI_Analytics.db
```

`GEMINI_API_KEY` e `GEMINI_MODEL` são opcionais para a coleta e para as estatísticas. Os endpoints de IA retornam erro `502` quando a chave não está configurada.

Nunca compartilhe ou registre suas chaves em arquivos versionados. O `.env` já está incluído no `.gitignore`.

## Executar a aplicação

Com o ambiente virtual ativado:

```powershell
uvicorn src.main:app --reload
```

Após iniciar o servidor:

- API: http://127.0.0.1:8000
- Dashboard: http://127.0.0.1:8000/static/index.html
- Documentação interativa: http://127.0.0.1:8000/docs

## Coletar partidas

Edite o PUUID em `TEST_PUUID`, dentro de `src/scripts/analytics.py`, e execute:

```powershell
python -m src.scripts.analytics
```

Por padrão, o coletor solicita até 50 partidas por execução e consulta os detalhes das partidas com até cinco requisições simultâneas. Partidas já existentes no banco são ignoradas.

É necessário configurar `RIOT_API_KEY` com uma chave válida.

## Dashboard

O dashboard possui três visualizações:

- **Winrate de Itens:** itens agrupados pela ordem de compra.
- **Winrate das Runas:** runas agrupadas por categoria.
- **Matchups:** winrate de Kindred contra cada jungler adversário.

Os itens usam imagens do Data Dragon; os nomes e metadados são obtidos dos catálogos locais presentes em `data/`.

## API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Status básico da aplicação. |
| `GET` | `/analytics/winrate/items` | Estatísticas de itens por ordem de compra. |
| `GET` | `/analytics/winrate/perks` | Estatísticas de runas por categoria e estilo. |
| `GET` | `/analytics/winrate/matchups` | Estatísticas contra junglers adversários. |
| `POST` | `/ai/items/analysis` | Análise de um item por IA. |
| `POST` | `/ai/perks/analysis` | Análise de uma runa por IA. |
| `GET` | `/ai/anomalies` | Busca anomalias nas estatísticas agregadas de itens. |
| `GET` | `/static/index.html` | Interface web do projeto. |
| `GET` | `/data/item.json` | Catálogo estático de itens. |
| `GET` | `/data/runesReforged.json` | Catálogo estático de runas. |

Exemplo de resposta para `/analytics/winrate/items`:

```json
[
  {
    "buy_order": 1,
    "item_name": "Glaive Sombria",
    "total_matches": 25,
    "wins": 14,
    "win_rate": 56.0
  }
]
```

Exemplo de corpo para `/ai/items/analysis`:

```json
{
  "item_name": "Glaive Sombria",
  "champion": "Kindred",
  "role": "Jungle",
  "patch": "26.23.1"
}
```

Exemplo de corpo para `/ai/perks/analysis`:

```json
{
  "perk_name": "Pressione o Ataque",
  "champion": "Kindred",
  "role": "Jungle",
  "patch": "26.23.1"
}
```

Quando não existem registros suficientes para uma consulta, os endpoints de estatística podem retornar uma lista vazia `[]`.

## Banco de dados

O banco padrão é `RiotAPI_Analytics.db`, criado automaticamente na primeira inicialização da aplicação ou do coletor.

As principais tabelas são:

| Tabela | Conteúdo |
|---|---|
| `matches` | ID, duração, vitória de Kindred e jungler adversário. |
| `item_partida` | Itens comprados em cada partida e sua ordem de compra. |
| `runa_partida` | Runas, categoria e estilo usados em cada partida. |

O banco é local e está excluído do controle de versão pelo `.gitignore`.

## Estrutura do projeto

```text
.
├── data/
│   ├── item.json                 # Catálogo local de itens
│   └── runesReforged.json        # Catálogo local de runas
├── src/
│   ├── main.py                   # Aplicação FastAPI e endpoints
│   ├── ia/
│   │   ├── ai_analytic.py        # Análise de itens com Gemini
│   │   └── ai_analytic_perks.py  # Análise de runas com Gemini
│   ├── model/
│   │   └── models.py             # Modelos SQLAlchemy
│   ├── repository/
│   │   ├── analyzeWinrate.py     # Agregação das estatísticas
│   │   ├── crud.py               # Persistência no banco
│   │   └── database.py           # Engine e sessões do SQLAlchemy
│   └── scripts/
│       ├── analytics.py          # Execução da coleta
│       └── riotApi.py            # Comunicação com Riot e Data Dragon local
├── static/
│   ├── index.html
│   ├── script.js
│   ├── perksAndMatchups.js
│   └── style.css
├── requirements.txt
└── RiotAPI_Analytics.db           # Banco SQLite local
```

## Observações

- Os dados são específicos de Kindred na jungle.
- Os resultados são agregações históricas armazenadas localmente, não dados ao vivo.
- A taxa de winrate por item considera cada registro de compra associado à partida.
- Runas do tipo `stat_shard` são removidas da análise de winrate de runas.
- A chave da Riot deve ser mantida privada e pode expirar conforme as regras da plataforma.
