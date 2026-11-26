# Riot API Analytics

Projeto de análise de dados competitivos de **Kindred Jungle** utilizando a API da Riot Games. A aplicação coleta partidas recentes, salva os dados em SQLite e apresenta estatísticas de itens, runas e confrontos em um dashboard web. Também oferece análises textuais com Google Gemini.

<p align="center">
  <img src="./static/kindred-fundo.gif" alt="Demonstração visual do dashboard" width="720">
</p>

## Visão geral

O projeto reúne três etapas principais:

1. coleta as partidas rankeadas Solo/Duo de uma conta pela Riot Match-V5 API;
2. filtra partidas válidas de Kindred na selva e salva itens, runas e o jungler adversário;
3. calcula win rates e disponibiliza os resultados em uma API REST e em um dashboard responsivo.

As informações exibidas são calculadas a partir do banco local. Elas não são atualizadas automaticamente em tempo real.

## Funcionalidades

- Coleta das 50 partidas rankeadas mais recentes de um PUUID.
- Filtro de partidas com duração mínima de 240 segundos.
- Identificação de partidas em que Kindred atuou na posição Jungle.
- Persistência local em SQLite.
- Evita duplicar partidas já armazenadas.
- Win rate por item e ordem de compra.
- Win rate por runa, categoria e estilo.
- Win rate por matchup contra cada jungler adversário.
- Dashboard web com abas para itens, runas e confrontos.
- Análise de itens, runas e matchups por Google Gemini.
- Documentação interativa da API com Swagger UI.
- Execução local com Python ou em contêiner Docker.

## Tecnologias utilizadas

| Área | Tecnologias |
|---|---|
| Backend | Python 3.10+, FastAPI, Uvicorn |
| Banco de dados | SQLite, SQLAlchemy |
| Dados | Pandas |
| Integrações | Riot Match-V5 API, HTTPX, Google Gen AI SDK |
| Configuração | python-dotenv |
| Interface | HTML5, CSS3, JavaScript |
| Implantação | Docker e Docker Compose |

## Pré-requisitos

### Execução local

- Python 3.10 ou superior.
- Uma chave da Riot Games Developer API.
- O PUUID da conta que será consultada.
- Uma chave Google Gemini para os recursos de IA.

### Execução com Docker

- Docker Desktop.
- Docker Compose.
- Arquivo `.env` configurado na raiz do projeto.

## Configuração

Crie o arquivo `.env` a partir do modelo:

```powershell
Copy-Item .env.example .env
```

Preencha as variáveis:

```dotenv
DATABASE_URL=sqlite:///./RiotAPI_Analytics.db
RIOT_API_KEY=sua_chave_da_riot
GEMINI_API_KEY=sua_chave_gemini
GEMINI_MODEL=gemini-3.5-flash-lite
RIOT_PUUID=seu_puuid
```

| Variável | Obrigatória | Descrição |
|---|---:|---|
| `RIOT_API_KEY` | Para coleta | Chave da Riot Match-V5 API. |
| `RIOT_PUUID` | Para coleta | PUUID da conta utilizada na busca das partidas. |
| `GEMINI_API_KEY` | Para IA | Chave usada pelas análises e pelos endpoints de anomalias. |
| `GEMINI_MODEL` | Não | Modelo Gemini. O padrão no código é `gemini-3.5-flash-lite`. |
| `DATABASE_URL` | Não | URL SQLAlchemy do banco. O padrão é o SQLite local do projeto. |

Não publique ou compartilhe as chaves. O arquivo `.env` não deve ser versionado.

## Instalação e execução local

Na raiz do repositório, execute:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```


Inicie a API e o dashboard:

```powershell
python -m uvicorn src.main:app --reload
```

Endereços locais:

- Dashboard: http://127.0.0.1:8000/static/index.html
- API: http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/docs

Verifique o status da API:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/"
```

Resposta esperada:

```json
{
  "status": "API is running",
  "project": "Riot API Analytics"
}
```

## Coleta de partidas

Com a chave Riot configurada e o PUUID definido em `RIOT_PUUID`, execute o coletor em outro terminal:

```powershell
python -m src.scripts.analytics
```

O processo:

1. consulta até 50 partidas da fila Solo/Duo (`queueId=420`);
2. baixa os dados pela região `americas`;
3. descarta partidas com menos de 240 segundos;
4. descarta partidas sem Kindred na posição Jungle;
5. converte IDs de itens e runas pelos catálogos locais em `data/`;
6. salva os dados novos no SQLite.

As partidas já presentes no banco são ignoradas. Execute o coletor novamente quando quiser incorporar partidas recentes novas.

## Execução com Docker

Crie o `.env` e execute na raiz do projeto:

```powershell
docker compose up --build
```

Para executar em segundo plano:

```powershell
docker compose up --build -d
```

O Compose publica o serviço em http://127.0.0.1:8000 e persiste o banco em um volume Docker chamado `riotapi_data`.

Para visualizar os contêineres:

```powershell
docker compose ps
```

Para encerrar o serviço:

```powershell
docker compose down
```

Para encerrar o serviço e remover também o volume do banco:

```powershell
docker compose down -v
```

Para executar a coleta de partidas dentro do contêiner:

```powershell
docker compose run --rm api python -m src.scripts.analytics
```

## Dashboard

Acesse http://127.0.0.1:8000/static/index.html.

O dashboard possui três visualizações:

- **Itens:** win rate por item e ordem de compra.
- **Runas:** win rate por runa, categoria e estilo.
- **Matchups:** win rate e desempenho contra cada jungler adversário.

Os cartões podem abrir uma análise detalhada. A análise depende de `GEMINI_API_KEY`.

## Exemplos de uso da API

### Estatísticas de itens

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/analytics/winrate/items"
```

Exemplo de resposta:

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

### Estatísticas de runas

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/analytics/winrate/perks"
```

### Estatísticas de matchups

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/analytics/winrate/matchups"
```

### Análise de item

```powershell
$body = @{
    item_name = "Glaive Sombria"
    champion = "Kindred"
    role = "Jungle"
    patch = "26.23.1"
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/ai/items/analysis" `
    -ContentType "application/json" `
    -Body $body
```

### Análise de runa

```powershell
$body = @{
    perk_name = "Pressione o Ataque"
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/ai/perks/analysis" `
    -ContentType "application/json" `
    -Body $body
```

### Análise de matchup

```powershell
$body = @{
    enemy_champion = "LeeSin"
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/ai/matchups/analysis" `
    -ContentType "application/json" `
    -Body $body
```

### Detecção de anomalias

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ai/anomalies"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ai/perks/anomalies"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ai/matchup/anomalies"
```

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Status da aplicação. |
| `GET` | `/analytics/winrate/items` | Win rate por item e ordem de compra. |
| `GET` | `/analytics/winrate/perks` | Win rate por runa. |
| `GET` | `/analytics/winrate/matchups` | Win rate contra junglers adversários. |
| `POST` | `/ai/items/analysis` | Analisa um item. |
| `POST` | `/ai/perks/analysis` | Analisa uma runa. |
| `POST` | `/ai/matchups/analysis` | Analisa um matchup. |
| `GET` | `/ai/anomalies` | Pesquisa anomalias em itens. |
| `GET` | `/ai/perks/anomalies` | Pesquisa anomalias em runas. |
| `GET` | `/ai/matchup/anomalies` | Pesquisa sinais em matchups. |
| `GET` | `/static/index.html` | Dashboard web. |
| `GET` | `/docs` | Documentação Swagger. |

## Banco de dados

O banco padrão é `RiotAPI_Analytics.db`. Ele é criado automaticamente na inicialização da aplicação.

| Tabela | Conteúdo |
|---|---|
| `matches` | ID, duração, vitória de Kindred e jungler adversário. |
| `item_partida` | Itens de cada partida e ordem de compra. |
| `runa_partida` | Runas, categoria e estilo de cada partida. |

Para usar outro banco SQLite ou PostgreSQL compatível com SQLAlchemy, altere `DATABASE_URL` no `.env`.

## Fluxo dos dados

```text
Riot API
   |
   v
src/scripts/riotApi.py
   |
   v
src/scripts/analytics.py
   |
   v
src/repository/crud.py -> SQLite
   |
   v
src/repository/analyzeWinrate.py
   |
   +---------------------------+
   v                           v
FastAPI REST               Dashboard web
   |
   v
Google Gemini
```

## Estrutura do projeto

```text
RiotAPI_Analytics/
├── data/
│   ├── champion.json
│   ├── item.json
│   └── runesReforged.json
├── src/
│   ├── ia/
│   ├── model/
│   ├── repository/
│   ├── scripts/
│   └── main.py
├── static/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   ├── perksAndMatchups.js
│   ├── detail-modal.js
│   └── kindred-fundo.gif
├── .env.example
├── compose.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Observações

- Stat shards não são incluídos nas estatísticas de runas.
- Os resultados dependem da quantidade de partidas armazenadas no banco.
- Análises com poucas partidas podem ser inconclusivas.
- O confronto é apenas uma referência exploratória e não determina sozinho o nível de dificuldade do matchup.
- Chaves da Riot podem expirar conforme as regras da plataforma.
