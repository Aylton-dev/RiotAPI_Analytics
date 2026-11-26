const ENDPOINTS = {
    runes: "/analytics/winrate/perks",
    matchups: "/analytics/winrate/matchups",
    runesJson: "/data/runesReforged.json",
    aiPerks: "/ai/perks/analysis",
    aiMatchups: "/ai/matchups/analysis",
};
const DDRAGON = "https://ddragon.leagueoflegends.com";
const CATEGORY_LABELS = {
    keystone: "Runa Principal",
    primary_runes: "Runas Primárias",
    secondary_runes: "Runas Secundárias",
};
const IMG_ERROR = "this.onerror=null; this.style.visibility='hidden';";

async function fetchJson(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Erro HTTP ${response.status} ao carregar ${url}`);
    }
    return response.json();
}

let ddragonVersionCache = null;

async function getDdragonVersion() {
    if (ddragonVersionCache) return ddragonVersionCache;

    const versions = await fetchJson(`${DDRAGON}/api/versions.json`);
    if (!Array.isArray(versions) || !versions[0]) {
        throw new Error("Não foi possível obter a versão do Data Dragon.");
    }

    ddragonVersionCache = versions[0];
    return ddragonVersionCache;
}

function formatWinrate(value) {
    const number = Number(value);
    return `${(Number.isFinite(number) ? number : 0).toFixed(1)}% WR`;
}

function buildRuneIconMap(runesJson) {
    const styles = Array.isArray(runesJson) ? runesJson : runesJson?.data || [];
    const map = {};

    for (const style of styles) {
        for (const slot of style.slots || []) {
            for (const rune of slot.runes || []) {
                map[rune.name] = rune.icon;
            }
        }
    }

    return map;
}

function groupByCategory(runes) {
    return runes.reduce((groups, rune) => {
        (groups[rune.category] ||= []).push(rune);
        return groups;
    }, {});
}

function getRuneIconUrl(iconPath) {
    return iconPath
        ? `${DDRAGON}/cdn/img/${iconPath.replace(/^\/+/, "")}`
        : "";
}

function getChampionIconUrl(version, championId) {
    return `${DDRAGON}/cdn/${version}/img/champion/${encodeURIComponent(championId)}.png`;
}

function mostrarErro(container, contexto, error) {
    const mensagem = document.createElement("p");
    mensagem.className = "error-msg";
    mensagem.textContent = `${contexto}: ${error.message || error}`;
    container.replaceChildren(mensagem);
}

function configurarEventosRunas(container) {
    if (!container || container.dataset.aiBound === "true") return;
    container.dataset.aiBound = "true";

    container.addEventListener("click", (event) => {
        const btn = event.target.closest(".icon-trigger[data-perk-name]");
        if (!btn || typeof window.abrirAnaliseIA !== "function") return;

        const perkName = btn.getAttribute("data-perk-name");
        if (!perkName) return;

        window.abrirAnaliseIA({
            endpoint: ENDPOINTS.aiPerks,
            payload: {
                perk_name: perkName,
                champion: "Kindred",
                role: "Jungle",
            },
            titulo: perkName,
            subtitulo: "Análise de Runa • Kindred Jungle",
            triggerEl: btn,
        });
    });
}

function configurarEventosMatchups(container) {
    if (!container || container.dataset.aiBound === "true") return;
    container.dataset.aiBound = "true";

    container.addEventListener("click", (event) => {
        const btn = event.target.closest(".icon-trigger[data-enemy-champion]");
        if (!btn || typeof window.abrirAnaliseIA !== "function") return;

        const enemyChampion = btn.getAttribute("data-enemy-champion");
        if (!enemyChampion) return;

        window.abrirAnaliseIA({
            endpoint: ENDPOINTS.aiMatchups,
            payload: {
                enemy_champion: enemyChampion,
                champion: "Kindred",
                role: "Jungle",
            },
            titulo: `vs. ${enemyChampion}`,
            subtitulo: "Análise de Matchup • Kindred Jungle",
            triggerEl: btn,
        });
    });
}

function renderRuneCard(rune, iconMap) {
    const imgUrl = getRuneIconUrl(iconMap[rune.perk_name]);
    return `
        <div class="item-card rune-card">
            <button
                type="button"
                class="icon-trigger"
                data-perk-name="${rune.perk_name}"
                aria-label="Analisar runa ${rune.perk_name} com IA"
            >
                <img src="${imgUrl}" alt="${rune.perk_name}" class="item-img" loading="lazy" onerror="${IMG_ERROR}">
            </button>
            <div class="item-info">
                <span class="item-name">${rune.perk_name}</span>
                <div class="item-stats">
                    <span>Partidas: <strong>${rune.total_matches}</strong></span>
                    <span class="item-winrate">${formatWinrate(rune.win_rate)}</span>
                </div>
            </div>
        </div>
    `;
}

async function carregarRunas(containerId = "runes-container") {
    const container = document.getElementById(containerId);
    if (!container) return;
    configurarEventosRunas(container);

    try {
        const [runes, runesJson] = await Promise.all([
            fetchJson(ENDPOINTS.runes),
            fetchJson(ENDPOINTS.runesJson),
        ]);

        if (runes.length === 0) {
            container.innerHTML = '<p class="empty-msg">Nenhum dado encontrado.</p>';
            return;
        }

        const iconMap = buildRuneIconMap(runesJson);
        const groups = groupByCategory(runes);

        container.innerHTML = Object.entries(groups).map(([category, list]) => `
            <h3 class="group-title">${CATEGORY_LABELS[category] || category}</h3>
            <div class="cards-grid">
                ${list.map(rune => renderRuneCard(rune, iconMap)).join("")}
            </div>
        `).join("");
    } catch (error) {
        console.error("Erro ao carregar runas:", error);
    }
}

function renderMatchupCard(matchup, version) {
    const imgUrl = getChampionIconUrl(version, matchup.enemy_jungler);
    const tooltip = `${matchup.enemy_jungler} - ${matchup.total_matches} partida(s)`;
    return `
        <div class="matchup-card" title="${tooltip}">
            <button
                type="button"
                class="icon-trigger"
                data-enemy-champion="${matchup.enemy_jungler}"
                aria-label="Analisar matchup contra ${matchup.enemy_jungler} com IA"
            >
                <img src="${imgUrl}" alt="${matchup.enemy_jungler}" class="matchup-img" loading="lazy" onerror="${IMG_ERROR}">
            </button>
            <span class="item-winrate">${formatWinrate(matchup.win_rate)}</span>
        </div>
    `;
}

async function carregarMatchups(containerId = "matchups-container") {
    const container = document.getElementById(containerId);
    if (!container) return;
    configurarEventosMatchups(container);

    try {
        const [matchups, version] = await Promise.all([
            fetchJson(ENDPOINTS.matchups),
            getDdragonVersion(),
        ]);

        if (matchups.length === 0) {
            container.innerHTML = '<p class="empty-msg">Nenhum dado encontrado.</p>';
            return;
        }

        container.innerHTML = matchups.map(m => renderMatchupCard(m, version)).join("");
    } catch (error) {
        console.error("Erro ao carregar matchups:", error);
    }
}