const API_BASE = "http://127.0.0.1:8000";

const ENDPOINTS = {
    runes: `${API_BASE}/analytics/winrate/perks`,
    matchups: `${API_BASE}/analytics/winrate/matchups`,
    runesJson: `${API_BASE}/data/runesReforged.json`,
};

const DDRAGON = "https://ddragon.leagueoflegends.com";

const CATEGORY_LABELS = {
    keystone: "Runa Principal",
    primary_runes: "Runas Primárias",
    secondary_runes: "Runas Secundárias",
};

async function fetchJson(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Erro ${response.status} em ${url}`);
    return response.json();
}

let versionCache = null;
async function getDdragonVersion() {
    if (versionCache) return versionCache;
    const versions = await fetchJson(`${DDRAGON}/api/versions.json`);
    versionCache = versions[0]; // a primeira é a mais recente
    return versionCache;
}

function formatWinrate(value) {
    return `${Number(value).toFixed(1)}% WR`;
}

const IMG_ERROR = `this.onerror=null; this.style.visibility='hidden';`;

function buildRuneIconMap(runesJson) {
    const map = {};
    for (const style of runesJson) {
        for (const slot of style.slots) {
            for (const rune of slot.runes) {
                map[rune.name] = rune.icon;
            }
        }
    }
    return map;
}

function getRuneIconUrl(iconPath) {
    return iconPath ? `${DDRAGON}/cdn/img/${iconPath}` : "";
}

function renderRuneCard(rune, iconMap) {
    const imgUrl = getRuneIconUrl(iconMap[rune.perk_name]);
    return `
        <div class="item-card rune-card">
            <img src="${imgUrl}" alt="${rune.perk_name}" class="item-img" loading="lazy" onerror="${IMG_ERROR}">
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

function groupByCategory(runes) {
    const groups = {};
    for (const rune of runes) {
        (groups[rune.category] ||= []).push(rune);
    }
    return groups;
}

async function carregarRunas(containerId = "runes-container") {
    const container = document.getElementById(containerId);
    if (!container) return;

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

function getChampionIconUrl(version, championId) {
    return `${DDRAGON}/cdn/${version}/img/champion/${championId}.png`;
}

function renderMatchupCard(matchup, version) {
    const imgUrl = getChampionIconUrl(version, matchup.enemy_jungler);
    const tooltip = `${matchup.enemy_jungler} - ${matchup.total_matches} partida(s)`;
    return `
        <div class="matchup-card" title="${tooltip}">
            <img src="${imgUrl}" alt="${matchup.enemy_jungler}" class="matchup-img" loading="lazy" onerror="${IMG_ERROR}">
            <span class="item-winrate">${formatWinrate(matchup.win_rate)}</span>
        </div>
    `;
}

async function carregarMatchups(containerId = "matchups-container") {
    const container = document.getElementById(containerId);
    if (!container) return;

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