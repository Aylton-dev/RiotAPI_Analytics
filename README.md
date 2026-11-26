# Riot API Analytics

Aplicação Python para coletar partidas de **Kindred na selva**, armazenar os dados localmente em SQLite e consultar estatísticas em um dashboard e em uma API REST.

A coleta usa a Riot Match-V5 API. O projeto agrega win rate por item e ordem de compra, runa e jungler adversário. O dashboard é servido pelo FastAPI; análises adicionais de itens, runas e matchups usam o Gemini.

## Funcionalidades

- Coleta de partidas ranqueadas solo/duo a partir de um PUUID.
- Filtro para partidas de pelo menos 240 segundos em que Kindred jogou na selva.
- Armazenamento de partidas, itens, runas e jungler adversário em SQLite; partidas já armazenadas são ignoradas.
- Estatísticas de win rate por item/ordem de compra, runa e matchup.
- Dashboard web com abas de itens, runas e matchups.
- Análises por IA de item, runa e matchup, além de endpoints de anomalias.

## Fluxo dos dados

1. `src/scripts/analytics.py` inicia a coleta usando o PUUID configurado em `TEST_PUUID`.
2. `src/scripts/riotApi.py` consulta os IDs de partidas na Riot Match-V5 API e busca os detalhes das partidas.
3. O coletor filtra partidas e converte IDs de itens/runas em nomes usando os arquivos JSON em `data/`.
4. `src/repository/crud.py` grava as partidas, itens e runas no SQLite por meio dos modelos SQLAlchemy em `src/model/models.py`.
5. `src/repository/analyzeWinrate.py` usa Pandas e consultas SQL para gerar as estatísticas consumidas pela API e pelo dashboard.
6. `src/main.py` expõe as rotas FastAPI, serve os arquivos de `static/` e conecta os endpoints de análise ao Gemini.

## Tecnologias

- Python 3.10+
- FastAPI e Uvicorn
- SQLAlchemy, SQLite e Pandas
- HTTPX e python-dotenv
- Google Gen AI SDK
- HTML, CSS e JavaScript

## Pré-requisitos

- Python 3.10 ou superior.
- Uma chave de desenvolvedor da Riot Games API para coletar partidas.
- O PUUID da conta a ser consultada.
- Uma chave Gemini (`GEMINI_API_KEY`) para usar as rotas de análise por IA.

## Instalação no Windows

Execute os comandos na raiz do repositório, onde ficam `requirements.txt` e as pastas `src/`, `data/` e `static/`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Confirme que a versão exibida é Python 3.10 ou superior.

Se o PowerShell bloquear a ativação do ambiente virtual, permita scripts somente na sessão atual e tente novamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Crie `.env` na raiz do projeto:

```dotenv
RIOT_API_KEY=sua_chave_da_riot
GEMINI_API_KEY=sua_chave_gemini
GEMINI_MODEL=gemini-3.5-flash-lite
DATABASE_URL=sqlite:///./RiotAPI_Analytics.db
```

`RIOT_API_KEY` é necessária para coletar partidas. `GEMINI_API_KEY` é necessária para as rotas de IA; ela não é necessária para iniciar a API ou consultar estatísticas já armazenadas. `GEMINI_MODEL` e `DATABASE_URL` são opcionais e têm valores padrão no código.

Não publique nem compartilhe chaves. `.env` já está listado no `.gitignore`.

## Executar a API e o dashboard

Com o ambiente virtual ativado, inicie o servidor na raiz do projeto:

```powershell
python -m uvicorn src.main:app --reload
```

Endereços locais:

- API: http://127.0.0.1:8000
- Dashboard: http://127.0.0.1:8000/static/index.html
- Documentação interativa da API: http://127.0.0.1:8000/docs

Verifique se a API iniciou:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/"
```

O dashboard exibe win rate de itens por ordem de compra, runas por categoria e matchups contra junglers adversários. Os botões de análise nas visualizações chamam os endpoints Gemini correspondentes.

## Coletar partidas

1. Abra `src/scripts/analytics.py` e substitua o valor de `TEST_PUUID` pelo PUUID da conta desejada.
2. Confirme que `RIOT_API_KEY` está configurada no `.env`.
3. Na raiz do projeto, com o ambiente virtual ativado, execute:

```powershell
python -m src.scripts.analytics
```

Cada execução solicita até 50 partidas da fila ranqueada solo/duo (`queueId=420`) pela rota regional `americas`. Os detalhes são consultados com até cinco requisições simultâneas. Partidas com menos de 240 segundos e partidas sem Kindred na selva são descartadas. Partidas já existentes no banco não são inseridas novamente.

O coletor usa os catálogos locais `data/item.json` e `data/runesReforged.json` para traduzir itens e runas. O processo não roda continuamente nem pagina para além das 50 partidas mais recentes: execute-o novamente para atualizar os dados depois que novas partidas estiverem disponíveis.

## Endpoints da API

### Estatísticas e catálogos

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Verifica se a API está ativa. |
| `GET` | `/analytics/winrate/items` | Win rate por item e ordem de compra. |
| `GET` | `/analytics/winrate/perks` | Win rate por runa, categoria e estilo. |
| `GET` | `/analytics/winrate/matchups` | Win rate contra cada jungler adversário. |
| `GET` | `/data/item.json` | Catálogo local de itens. |
| `GET` | `/data/champion.json` | Catálogo local de campeões. |
| `GET` | `/data/runesReforged.json` | Catálogo local de runas. |
| `GET` | `/static/index.html` | Dashboard web. |

Exemplos de consulta no PowerShell:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/analytics/winrate/items"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/analytics/winrate/perks"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/analytics/winrate/matchups"
```

Exemplo de resposta de estatística:

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

### Análises com IA

| Método | Rota | Campo obrigatório | Descrição |
|---|---|---|---|
| `POST` | `/ai/items/analysis` | `item_name` | Analisa um item. |
| `POST` | `/ai/perks/analysis` | `perk_name` | Analisa uma runa. |
| `POST` | `/ai/matchups/analysis` | `enemy_champion` | Analisa um matchup. |
| `GET` | `/ai/anomalies` | — | Detecta possíveis anomalias nas estatísticas de itens. |
| `GET` | `/ai/perks/anomalies` | — | Detecta possíveis anomalias nas estatísticas de runas. |
| `GET` | `/ai/matchup/anomalies` | — | Detecta sinais estatísticos nos matchups. |

Os campos `champion`, `role` e `patch` são opcionais nas requisições `POST`; os valores padrão são `Kindred`, `Jungle` e `26.23.1`.

Exemplos executáveis no PowerShell:

```powershell
$itemBody = @{
    item_name = "Glaive Sombria"
    champion = "Kindred"
    role = "Jungle"
    patch = "26.23.1"
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/ai/items/analysis" `
    -ContentType "application/json" `
    -Body $itemBody
```

```powershell
$perkBody = @{
    perk_name = "Pressione o Ataque"
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/ai/perks/analysis" `
    -ContentType "application/json" `
    -Body $perkBody
```

```powershell
$matchupBody = @{
    enemy_champion = "LeeSin"
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/ai/matchups/analysis" `
    -ContentType "application/json" `
    -Body $matchupBody
```

Para consultar anomalias, por exemplo:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ai/matchup/anomalies"
```

O formato dos relatórios de anomalia é:

```json
{
  "anomalias": [
    {
      "item_name": "Kayn",
      "tipo_anomalia": "Win rate extremo com amostra reduzida",
      "motivo": "Win rate observado de 25.00% (3 vitórias em 12 partidas). A amostra está abaixo de 15 partidas; o sinal é inconclusivo."
    }
  ]
}
```

As rotas de IA precisam de `GEMINI_API_KEY`. Campeões, itens ou runas não encontrados podem retornar `404`; falhas de configuração ou do provedor de IA retornam `502`. Quando não há dados ou sinais que atendam aos critérios, uma rota de estatísticas/anomalias pode retornar uma lista vazia.

## Banco de dados

O banco padrão é `RiotAPI_Analytics.db`, no diretório de execução, e as tabelas são criadas automaticamente pela aplicação ou pelo coletor. Para usar outro banco, defina `DATABASE_URL` no `.env`.

| Tabela | Conteúdo |
|---|---|
| `matches` | ID, duração, vitória de Kindred e jungler adversário. |
| `item_partida` | Itens da partida e ordem de compra. |
| `runa_partida` | Runas, categoria e estilo usados na partida. |

O banco SQLite local é ignorado pelo Git.

## Estrutura do projeto

```text
.
├── data/
│   ├── champion.json             # Catálogo local de campeões
│   ├── item.json                 # Catálogo local de itens
│   └── runesReforged.json        # Catálogo local de runas
├── src/
│   ├── main.py                   # Aplicação FastAPI e rotas
│   ├── ia/
│   │   ├── ai_analytic.py        # Análise e anomalias de itens
│   │   ├── ai_analytic_matchup.py # Análise e anomalias de matchups
│   │   └── ai_analytic_perks.py  # Análise e anomalias de runas
│   ├── model/
│   │   └── models.py             # Modelos SQLAlchemy
│   ├── repository/
│   │   ├── analyzeWinrate.py     # Agregações estatísticas
│   │   ├── crud.py               # Persistência das partidas
│   │   └── database.py           # Engine e sessões SQLAlchemy
│   └── scripts/
│       ├── analytics.py          # Entrada do coletor
│       └── riotApi.py            # Requisições Riot e tradução dos dados
├── static/                       # Dashboard HTML, CSS e JavaScript
├── requirements.txt
└── README.md
```

## Observações

- As estatísticas são agregações históricas do banco local, não dados ao vivo.
- A análise de itens considera a ordem de compra registrada.
- Runas `stat_shard` são excluídas das estatísticas de win rate de runas.
- O alerta de matchup com baixa amostra é exploratório: exige pelo menos quatro partidas e win rate de até 25% ou a partir de 75%; não confirma, por si só, a dificuldade do confronto.
- Mantenha as chaves da Riot e do Gemini privadas. Chaves de desenvolvedor da Riot podem expirar conforme as regras da plataforma.
