(() => {
  const cache = new Map();
  let lastTrigger = null;

  const FIELD_CONFIG = {
    "/ai/items/analysis": [
      { key: "perfil_item", label: "Perfil do Item", type: "text" },
      { key: "impacto_no_jogo", label: "Impacto no Jogo", type: "text" },
      { key: "momento_de_compra", label: "Momento de Compra", type: "text" },
      { key: "alternativas", label: "Alternativas", type: "list" },
      { key: "ressalvas", label: "Ressalvas", type: "list" },
    ],
    "/ai/perks/analysis": [
      { key: "foco_de_jogo", label: "Foco de Jogo", type: "text" },
      { key: "o_que_a_runa_faz", label: "O Que a Runa Faz", type: "text" },
      { key: "melhor_contexto", label: "Melhor Contexto", type: "text" },
      { key: "melhor_situacao_de_uso", label: "Melhor Situação de Uso", type: "text" },
    ],
    "/ai/matchups/analysis": [
      { key: "classificacao_matchup", label: "Classificação do Matchup", type: "text" },
      { key: "dinamica_do_matchup", label: "Dinâmica do Matchup", type: "text" },
      { key: "ritmo_e_estagio", label: "Ritmo e Estágio", type: "text" },
      { key: "como_jogar_contra", label: "Como Jogar Contra", type: "text" },
      { key: "dica_de_execucao", label: "Dica de Execução", type: "text" },
    ],
  };

  function getElements() {
    const dialog = document.getElementById("ai-detail-modal");
    if (!dialog) return null;
    return {
      dialog,
      title: document.getElementById("ai-modal-title"),
      subtitle: document.getElementById("ai-modal-subtitle"),
      closeBtn: document.getElementById("ai-modal-close"),
      loading: document.getElementById("ai-modal-loading"),
      error: document.getElementById("ai-modal-error"),
      empty: document.getElementById("ai-modal-empty"),
      content: document.getElementById("ai-modal-content"),
    };
  }

  function setState(els, stateName) {
    els.loading.hidden = stateName !== "loading";
    els.error.hidden = stateName !== "error";
    els.empty.hidden = stateName !== "empty";
    els.content.hidden = stateName !== "content";
  }

  function renderData(els, endpoint, data) {
    els.content.replaceChildren();
    const sections = FIELD_CONFIG[endpoint] || [];
    let renderedCount = 0;

    for (const cfg of sections) {
      const val = data?.[cfg.key];
      if (val === null || val === undefined) continue;

      if (cfg.type === "list") {
        if (!Array.isArray(val) || val.length === 0) continue;
        const box = document.createElement("section");
        box.className = "ai-section";

        const lbl = document.createElement("span");
        lbl.className = "ai-section-label";
        lbl.textContent = cfg.label;

        const ul = document.createElement("ul");
        ul.className = "ai-section-list";
        for (const item of val) {
          const li = document.createElement("li");
          li.textContent = String(item);
          ul.appendChild(li);
        }

        box.append(lbl, ul);
        els.content.appendChild(box);
        renderedCount += 1;
      } else {
        const text = String(val).trim();
        if (!text) continue;

        const box = document.createElement("section");
        box.className = "ai-section";

        const lbl = document.createElement("span");
        lbl.className = "ai-section-label";
        lbl.textContent = cfg.label;

        const p = document.createElement("p");
        p.className = "ai-section-text";
        p.textContent = text;

        box.append(lbl, p);
        els.content.appendChild(box);
        renderedCount += 1;
      }
    }

    if (renderedCount === 0) {
      setState(els, "empty");
    } else {
      setState(els, "content");
    }
  }

  function bindDialogEventsOnce(els) {
    if (els.dialog.dataset.bound === "true") return;
    els.dialog.dataset.bound = "true";

    els.closeBtn?.addEventListener("click", () => {
      els.dialog.close();
    });

    els.dialog.addEventListener("click", (event) => {
      if (event.target === els.dialog) {
        els.dialog.close();
      }
    });

    els.dialog.addEventListener("close", () => {
      if (lastTrigger && lastTrigger.isConnected) {
        lastTrigger.focus();
      }
      lastTrigger = null;
    });
  }

  async function abrirAnaliseIA({ endpoint, payload, titulo, subtitulo, triggerEl = null }) {
    const els = getElements();
    if (!els) return;
    bindDialogEventsOnce(els);

    if (triggerEl instanceof HTMLElement) {
      lastTrigger = triggerEl;
    }

    els.title.textContent = titulo || "Análise com IA";
    els.subtitle.textContent = subtitulo || "";
    els.error.textContent = "";
    setState(els, "loading");

    if (!els.dialog.open) {
      els.dialog.showModal();
    }

    const cacheKey = `${endpoint}::${JSON.stringify(payload)}`;
    if (cache.has(cacheKey)) {
      renderData(els, endpoint, cache.get(cacheKey));
      return;
    }

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      let body = null;
      try {
        body = await response.json();
      } catch {
        body = null;
      }

      if (!response.ok) {
        const detail =
          (body && typeof body.detail === "string" && body.detail) ||
          `Erro HTTP ${response.status} ao consultar ${endpoint}.`;
        els.error.textContent = detail;
        setState(els, "error");
        return;
      }

      cache.set(cacheKey, body);
      renderData(els, endpoint, body);
    } catch {
      els.error.textContent = "Falha de rede ao conectar com o servidor.";
      setState(els, "error");
    }
  }

  window.abrirAnaliseIA = abrirAnaliseIA;
})();