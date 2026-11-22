async function carregarDados(tipo) {
    if (tipo !== 'itens') return;

    try {
        const [responseApi, responseJsonRiot] = await Promise.all([
            fetch('http://127.0.0.1:8000/analytics/winrate/items'),
            fetch('http://127.0.0.1:8000/data/item.json')
        ]);

        const dataApi = await responseApi.json();
        const riotJson = await responseJsonRiot.json();

        const version = riotJson.version;
        const baseImg = `https://ddragon.leagueoflegends.com/cdn/${version}/img/item`;

        
        const mapaImagens = {};
        for (const info of Object.values(riotJson.data)) {
            if (info.maps && info.maps["11"] === false) continue;
            if (info.gold && info.gold.purchasable === false) continue;
            if (!mapaImagens[info.name]) {
                mapaImagens[info.name] = info.image.full; // ex: "3033.png"
            }
        }

        const container = document.getElementById('items-container');

        if (dataApi.length === 0) {
            container.innerHTML = '<p style="color: #94a3b8; text-align: center; grid-column: 1/-1;">Nenhum dado encontrado.</p>';
            return;
        }

        container.innerHTML = dataApi.map(item => {
            const nomeItem = item.item_name;
            const arquivo = mapaImagens[nomeItem];
            const imgUrl = arquivo ? `${baseImg}/${arquivo}` : '';

            return `
                <div class="item-card">
                    <img src="${imgUrl}" alt="${nomeItem}" class="item-img" loading="lazy"
                         onerror="this.onerror=null; this.style.visibility='hidden';">
                    <div class="item-info">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="item-name">${nomeItem}</span>
                            <span class="item-slot-badge">FEITO: ${item.buy_order}º</span>
                        </div>
                        <div class="item-stats">
                            <span>Partidas: <strong>${item.total_matches}</strong></span>
                            <span class="item-winrate">${Number(item.win_rate).toFixed(1)}% WR</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

    } catch (error) {
        console.error("Erro ao carregar os dados ou o item.json:", error);
    }
}

function avisoScriptFaltando(containerId) {
    const el = document.getElementById(containerId);
    if (el) {
        el.innerHTML = '<p style="color:#f87171">Não foi possível carregar o runesMatchups.js. ' +
                       'Verifique o caminho do &lt;script&gt; no index.html.</p>';
    }
}

const ABAS = {
    itens: {
        container: 'items-container',
        apelidos: ['itens', 'items'],
        carregar: () => carregarDados('itens'),
    },
    runas: {
        container: 'runes-container',
        apelidos: ['runas', 'runes'],
        carregar: () => typeof carregarRunas === 'function'
            ? carregarRunas()
            : avisoScriptFaltando('runes-container'),
    },
    matchups: {
        container: 'matchups-container',
        apelidos: ['matchups', 'matchup'],
        carregar: () => typeof carregarMatchups === 'function'
            ? carregarMatchups()
            : avisoScriptFaltando('matchups-container'),
    },
};

const TITULOS = {
    itens: 'Winrate dos Itens',
    runas: 'Winrate das Runas',
    matchups: 'Winrate dos Matchups',
};

const abasCarregadas = new Set();
let abaAtual = null;              

function resolverAba(nome) {
    const n = String(nome).trim().toLowerCase();
    return Object.keys(ABAS).find(chave => ABAS[chave].apelidos.includes(n)) || null;
}

function getPainel(chave) {
    const container = document.getElementById(ABAS[chave].container);
    if (!container) return null;
    return container.closest('[id^="painel-"]') || container;
}

function mudarAba(nome) {
    const escolhida = resolverAba(nome);
    if (!escolhida) {
        console.warn(`mudarAba: aba desconhecida "${nome}"`);
        return;
    }

    const bloco = document.querySelector('.glass-panel');

    if (escolhida === abaAtual) {
        if (bloco) bloco.style.display = 'none';
        document.querySelectorAll('button').forEach(btn => btn.classList.remove('active'));
        abaAtual = null;
        return;
    }

    
    if (bloco) bloco.style.display = '';
    abaAtual = escolhida;

    const titulo = document.getElementById('panel-title');
    if (titulo) titulo.textContent = TITULOS[escolhida];

    for (const chave of Object.keys(ABAS)) {
        const painel = getPainel(chave);
        if (painel) painel.style.display = (chave === escolhida) ? '' : 'none';
    }

    document.querySelectorAll('button').forEach(btn => {
        const onclick = (btn.getAttribute('onclick') || '').toLowerCase();
        const ehDestaAba = ABAS[escolhida].apelidos.some(a => onclick.includes(`'${a}'`) || onclick.includes(`"${a}"`));
        btn.classList.toggle('active', ehDestaAba);
    });

    if (!abasCarregadas.has(escolhida)) {
        abasCarregadas.add(escolhida);
        ABAS[escolhida].carregar();
    }
}

document.addEventListener('DOMContentLoaded', () => mudarAba('itens'));