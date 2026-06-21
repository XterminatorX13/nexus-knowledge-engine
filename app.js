/**
 * Nexus Knowledge Engine — app.js
 * Interface de Busca Facetada + Navegação Semântica
 * 
 * Consome: dados_enriquecidos.json + vocabulario.json
 */

// ============================================================================
// STATE
// ============================================================================
let enrichedData = null;
let vocabulario = null;
let allFiles = [];         // Flat list of all file nodes (for search/filter)
let activeFacets = {};     // { dominio: "business", formato: "imagem", ... }
let activeTagFilters = []; // ["beriam", "moda"]
let currentView = "gallery";
let currentDensity = "comfortable";
let selectedItem = null;

const ICONS = {
    pasta: "📁", imagem: "🖼️", documento: "📝", planilha: "📊",
    video: "🎥", audio: "🎵", codigo: "💻", compactado: "📦",
    atalho: "🔗", fonte: "🔤", outro: "📄"
};

// ============================================================================
// DATA LOADING & FLATTENING
// ============================================================================

function flattenTree(node, result = []) {
    if (node.type === "file") {
        result.push(node);
    }
    if (node.children) {
        for (const child of node.children) {
            flattenTree(child, result);
        }
    }
    return result;
}

function buildFacetCounts() {
    const counts = {
        dominio: {}, formato: {}, status: {}, ferramentas: {}, tags: {}
    };

    for (const file of allFiles) {
        // Domínio
        const d = file.facets.dominio;
        counts.dominio[d] = (counts.dominio[d] || 0) + 1;

        // Formato
        const m = file.facets.formato;
        counts.formato[m] = (counts.formato[m] || 0) + 1;

        // Status
        const e = file.facets.status;
        counts.status[e] = (counts.status[e] || 0) + 1;

        // Tags
        for (const tag of file.tags || []) {
            counts.tags[tag] = (counts.tags[tag] || 0) + 1;
        }
    }

    return counts;
}

// ============================================================================
// FILTERING ENGINE
// ============================================================================

function getFilteredFiles() {
    return allFiles.filter(file => {
        // Check facet filters
        for (const [facetKey, facetValue] of Object.entries(activeFacets)) {
            if (facetKey === "ferramentas") {
                if (!file.facets.ferramentas || !file.facets.ferramentas.includes(facetValue)) return false;
            } else {
                if (file.facets[facetKey] !== facetValue) return false;
            }
        }

        // Check tag filters (intersection — file must have ALL active tags)
        for (const tag of activeTagFilters) {
            if (!file.tags || !file.tags.includes(tag)) return false;
        }

        return true;
    });
}

// ============================================================================
// SIDEBAR: FACET PANELS
// ============================================================================

function renderFacets() {
    const counts = buildFacetCounts();

    // Smart Collections
    const scContainer = document.getElementById("smartCollections");
    if (vocabulario && vocabulario.smart_collections) {
        let html = "";
        const collectionLabels = {
            "gerado-por-ia": "🤖 Gerado por IA",
            "screenshots": "📸 Screenshots",
            "pendentes-inbox": "📥 Pendentes (Inbox)",
            "arquivo-morto": "🗃️ Arquivo Morto",
            "pastas-vazias": "🕳️ Pastas Vazias"
        };
        for (const [key, data] of Object.entries(vocabulario.smart_collections)) {
            const label = collectionLabels[key] || key;
            html += `<button class="facet-btn" data-collection="${key}">${label} <span class="facet-count">${data.total}</span></button>`;
        }
        scContainer.innerHTML = html;
    }

    // Domain
    renderFacetGroup("facetDomain", counts.dominio, "dominio", {
        "business": "💼 Negócios",
        "estudo": "📚 Estudo",
        "games": "🎮 Games",
        "pessoal": "👤 Pessoal",
        "criativo": "🎨 Criativo",
        "arquivo": "🗄️ Arquivo",
        "inbox": "📥 Inbox",
        "indefinido": "❓ Indefinido"
    });

    // Format
    renderFacetGroup("facetFormat", counts.formato, "formato", {
        "imagem": "🖼️ Imagem",
        "documento": "📝 Documento",
        "planilha": "📊 Planilha",
        "codigo": "💻 Código",
        "video": "🎥 Vídeo",
        "audio": "🎵 Áudio",
        "compactado": "📦 Compactado",
        "fonte": "🔤 Fonte",
        "atalho": "🔗 Atalho",
        "outro": "📄 Outro"
    });

    // Status
    renderFacetGroup("facetStatus", counts.status, "status", {
        "ativo": "🟢 Ativo",
        "arquivado": "🟡 Arquivado",
        "pendente": "🔴 Pendente",
        "referência": "🔵 Referência",
        "rascunho": "⚪ Rascunho"
    });
}

function renderFacetGroup(containerId, counts, facetKey, labels) {
    const container = document.getElementById(containerId);
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    let html = "";
    for (const [value, count] of sorted) {
        if (count === 0) continue;
        const label = labels[value] || value;
        const isActive = activeFacets[facetKey] === value;
        html += `<button class="facet-btn ${isActive ? 'active' : ''}" data-facet="${facetKey}" data-value="${value}">
            ${label} <span class="facet-count">${count.toLocaleString()}</span>
        </button>`;
    }
    container.innerHTML = html;
}

// ============================================================================
// TAG CLOUD
// ============================================================================

function renderTagCloud() {
    const filtered = getFilteredFiles();
    const tagCounts = {};
    for (const f of filtered) {
        for (const tag of f.tags || []) {
            // Exclude facet values already being filtered (avoid redundancy)
            if (Object.values(activeFacets).includes(tag)) continue;
            tagCounts[tag] = (tagCounts[tag] || 0) + 1;
        }
    }

    const top = Object.entries(tagCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 30);

    const container = document.getElementById("tagCloud");
    if (top.length === 0) {
        container.innerHTML = "";
        return;
    }

    const maxCount = top[0][1];
    let html = "";
    for (const [tag, count] of top) {
        const size = 0.7 + (count / maxCount) * 0.6; // Scale 0.7rem to 1.3rem
        const isActive = activeTagFilters.includes(tag);
        html += `<button class="tag-pill ${isActive ? 'active' : ''}" data-tag="${tag}" style="font-size:${size}rem">${tag} <span class="tag-count">${count}</span></button>`;
    }
    container.innerHTML = html;
}

// ============================================================================
// ACTIVE FILTERS DISPLAY
// ============================================================================

function renderActiveFilters() {
    const container = document.getElementById("activeFilters");
    const parts = [];

    for (const [key, val] of Object.entries(activeFacets)) {
        parts.push(`<span class="active-chip" data-remove-facet="${key}">${key}: ${val} ✕</span>`);
    }
    for (const tag of activeTagFilters) {
        parts.push(`<span class="active-chip tag-chip" data-remove-tag="${tag}">#${tag} ✕</span>`);
    }

    if (parts.length === 0) {
        const filtered = getFilteredFiles();
        container.innerHTML = `<span class="filter-label">${filtered.length.toLocaleString()} arquivos</span>`;
    } else {
        const filtered = getFilteredFiles();
        container.innerHTML = `<span class="filter-label">${filtered.length.toLocaleString()} resultados →</span> ${parts.join("")}`;
    }
}

// ============================================================================
// MAIN RENDERERS
// ============================================================================

function renderMainPanel() {
    const container = document.getElementById("contentPreview");
    container.innerHTML = "";
    const filtered = getFilteredFiles();

    renderActiveFilters();
    renderTagCloud();

    if (currentView === "graph") {
        renderGraph(container, filtered);
    } else if (currentView === "list") {
        renderList(container, filtered);
    } else {
        renderGallery(container, filtered);
    }
}

function renderGallery(container, files) {
    if (files.length === 0) {
        container.innerHTML = `<div class="empty-state"><div class="empty-icon">🔍</div><h3>Nenhum resultado</h3><p>Ajuste os filtros para encontrar arquivos.</p></div>`;
        return;
    }

    const limit = 500; // Performance guard
    const showing = files.slice(0, limit);

    let html = `<div class="gallery-view">`;
    for (const file of showing) {
        const icon = ICONS[file.facets.formato] || ICONS.outro;
        const tags = (file.tags || []).slice(0, 3).map(t => `<span class="gallery-tag">#${t}</span>`).join("");
        html += `
            <div class="gallery-item" data-path="${file.path}">
                <div class="gallery-icon">${icon}</div>
                <div class="gallery-name" title="${file.name}">${file.name}</div>
                <div class="gallery-tags">${tags}</div>
            </div>`;
    }
    html += `</div>`;
    if (files.length > limit) {
        html += `<div class="load-more-hint">${files.length - limit} itens adicionais ocultos. Refine os filtros.</div>`;
    }
    container.innerHTML = html;
}

function renderList(container, files) {
    if (files.length === 0) {
        container.innerHTML = `<div class="empty-state"><div class="empty-icon">🔍</div><h3>Nenhum resultado</h3></div>`;
        return;
    }

    const limit = 1000;
    const showing = files.slice(0, limit);

    let html = `<table class="list-view">
        <thead><tr><th>Nome</th><th>Formato</th><th>Domínio</th><th>Tags</th></tr></thead>
        <tbody>`;
    for (const file of showing) {
        const icon = ICONS[file.facets.formato] || ICONS.outro;
        const tags = (file.tags || []).slice(0, 4).join(", ");
        html += `
            <tr class="list-row" data-path="${file.path}">
                <td><span class="list-icon">${icon}</span> <span class="list-name">${file.name}</span></td>
                <td><span class="list-type">${file.facets.formato}</span></td>
                <td><span class="list-type">${file.facets.dominio}</span></td>
                <td><span class="list-type">${tags}</span></td>
            </tr>`;
    }
    html += `</tbody></table>`;
    if (files.length > limit) {
        html += `<div class="load-more-hint">${files.length - limit} itens ocultos.</div>`;
    }
    container.innerHTML = html;
}

// ============================================================================
// D3 GRAPH VIEW
// ============================================================================

let d3Simulation = null;

function renderGraph(container, files) {
    container.innerHTML = `<div class="graph-view-container" id="graphContainer"><svg id="d3-svg"></svg><div id="graph-tooltip" class="graph-tooltip"></div></div>`;

    const width = container.clientWidth;
    const height = container.clientHeight;
    if (!width || !height) return;

    const svg = d3.select("#d3-svg").attr("viewBox", [0, 0, width, height]);
    const g = svg.append("g");
    svg.call(d3.zoom().extent([[0, 0], [width, height]]).scaleExtent([0.1, 8]).on("zoom", (e) => g.attr("transform", e.transform)));

    const tooltip = d3.select("#graph-tooltip");

    // Build graph data: group files by their top tag
    const tagGroups = {};
    const sample = files.slice(0, 300); // Performance limit

    for (const file of sample) {
        const mainTag = (file.tags && file.tags.length > 0) ? file.tags[0] : "sem-tag";
        if (!tagGroups[mainTag]) tagGroups[mainTag] = [];
        tagGroups[mainTag].push(file);
    }

    const nodes = [];
    const links = [];
    const colors = d3.scaleOrdinal(d3.schemeTableau10);

    // Add tag hub nodes
    let i = 0;
    for (const [tag, tagFiles] of Object.entries(tagGroups)) {
        const hubId = `hub-${tag}`;
        nodes.push({ id: hubId, name: tag, type: "hub", radius: 14 + Math.min(tagFiles.length, 30), color: colors(i) });

        for (const file of tagFiles.slice(0, 50)) {
            const fileId = file.path;
            nodes.push({ id: fileId, name: file.name, type: "file", radius: 4, color: colors(i), fileData: file });
            links.push({ source: hubId, target: fileId });
        }
        i++;
    }

    if (d3Simulation) d3Simulation.stop();

    d3Simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(d => d.source.type === "hub" ? 60 : 30))
        .force("charge", d3.forceManyBody().strength(d => d.type === "hub" ? -200 : -15))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collide", d3.forceCollide().radius(d => d.radius + 3));

    const linkEls = g.append("g").selectAll("line").data(links).join("line").attr("class", "link");
    const nodeEls = g.append("g").selectAll("circle").data(nodes).join("circle")
        .attr("class", "node").attr("r", d => d.radius).attr("fill", d => d.color)
        .call(d3.drag()
            .on("start", (e) => { if (!e.active) d3Simulation.alphaTarget(0.3).restart(); e.subject.fx = e.subject.x; e.subject.fy = e.subject.y; })
            .on("drag", (e) => { e.subject.fx = e.x; e.subject.fy = e.y; })
            .on("end", (e) => { if (!e.active) d3Simulation.alphaTarget(0); e.subject.fx = null; e.subject.fy = null; })
        )
        .on("mouseover", (event, d) => {
            tooltip.style("opacity", 1).html(`<strong>${d.name}</strong><br>${d.type === "hub" ? "Tag" : "Arquivo"}`).style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 10) + "px");
        })
        .on("mouseout", () => tooltip.style("opacity", 0))
        .on("click", (event, d) => {
            if (d.type === "hub") {
                toggleTag(d.name.replace("hub-", ""));
            } else if (d.fileData) {
                showDetail(d.fileData);
            }
        });

    const labels = g.append("g").selectAll("text").data(nodes.filter(d => d.type === "hub")).join("text")
        .attr("class", "node-label").attr("dx", 18).attr("dy", 4).text(d => d.name);

    d3Simulation.on("tick", () => {
        linkEls.attr("x1", d => d.source.x).attr("y1", d => d.source.y).attr("x2", d => d.target.x).attr("y2", d => d.target.y);
        nodeEls.attr("cx", d => d.x).attr("cy", d => d.y);
        labels.attr("x", d => d.x).attr("y", d => d.y);
    });
}

// ============================================================================
// DETAIL MODAL
// ============================================================================

function showDetail(file) {
    const modal = document.getElementById("detailModal");
    const body = document.getElementById("modalBody");
    const icon = ICONS[file.facets.formato] || ICONS.outro;
    const tags = (file.tags || []).map(t => `<span class="detail-tag">#${t}</span>`).join(" ");

    // Tesauro lookup
    let thesaurusHtml = "";
    if (vocabulario && vocabulario.termos) {
        for (const tag of file.tags || []) {
            const entry = vocabulario.termos[tag];
            if (entry) {
                thesaurusHtml += `
                <div class="thesaurus-entry">
                    <strong>${entry.label}</strong>
                    ${entry.sinonimos && entry.sinonimos.length ? `<div class="thes-row">≈ Sinônimos: ${entry.sinonimos.join(", ")}</div>` : ""}
                    ${entry.categoria_pai ? `<div class="thes-row">📂 Categoria Pai: ${entry.categoria_pai}</div>` : ""}
                    ${entry.subcategorias && entry.subcategorias.length ? `<div class="thes-row">🏷️ Subcategorias: ${entry.subcategorias.join(", ")}</div>` : ""}
                    ${entry.relacionados && entry.relacionados.length ? `<div class="thes-row">🔗 Relacionados: ${entry.relacionados.join(", ")}</div>` : ""}
                </div>`;
            }
        }
    }

    body.innerHTML = `
        <div class="detail-view">
            <div class="detail-icon">${icon}</div>
            <h3 class="detail-title">${file.name}</h3>
            <div class="detail-meta">${file.facets.formato} · ${file.facets.dominio} · ${file.facets.status}</div>
            <div class="detail-path">${file.path}</div>
            <button class="btn-copy" onclick="copyPath('${file.path.replace(/'/g, "\\'")}')">📋 Copiar Caminho</button>
            <div class="detail-tags">${tags}</div>
            ${thesaurusHtml ? `<div class="thesaurus-section"><h4>📖 Tesauro</h4>${thesaurusHtml}</div>` : ""}
        </div>`;
    modal.style.display = "flex";
}

window.copyPath = function(path) {
    navigator.clipboard.writeText(path).then(() => {
        const toast = document.getElementById("toast");
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 2000);
    });
};

// ============================================================================
// EVENT HANDLERS
// ============================================================================

function toggleFacet(facetKey, facetValue) {
    if (activeFacets[facetKey] === facetValue) {
        delete activeFacets[facetKey];
    } else {
        activeFacets[facetKey] = facetValue;
    }
    renderFacets();
    renderMainPanel();
}

function toggleTag(tag) {
    const idx = activeTagFilters.indexOf(tag);
    if (idx >= 0) {
        activeTagFilters.splice(idx, 1);
    } else {
        activeTagFilters.push(tag);
    }
    renderMainPanel();
}

function clearAllFilters() {
    activeFacets = {};
    activeTagFilters = [];
    renderFacets();
    renderMainPanel();
}

function setView(view) {
    currentView = view;
    document.querySelectorAll(".view-btn").forEach(btn => btn.classList.toggle("active", btn.dataset.view === view));
    const dc = document.getElementById("densityControls");
    dc.style.display = view === "gallery" ? "flex" : "none";
    renderMainPanel();
}

// Delegated Event Listeners
document.addEventListener("click", (e) => {
    // Facet buttons
    const facetBtn = e.target.closest(".facet-btn[data-facet]");
    if (facetBtn) {
        toggleFacet(facetBtn.dataset.facet, facetBtn.dataset.value);
        return;
    }

    // Smart Collections
    const collBtn = e.target.closest(".facet-btn[data-collection]");
    if (collBtn) {
        // TODO: implement collection view
        return;
    }

    // Tag pills
    const tagPill = e.target.closest(".tag-pill");
    if (tagPill) {
        toggleTag(tagPill.dataset.tag);
        return;
    }

    // Active filter chips (remove)
    const removeChip = e.target.closest("[data-remove-facet]");
    if (removeChip) {
        delete activeFacets[removeChip.dataset.removeFacet];
        renderFacets();
        renderMainPanel();
        return;
    }
    const removeTag = e.target.closest("[data-remove-tag]");
    if (removeTag) {
        activeTagFilters = activeTagFilters.filter(t => t !== removeTag.dataset.removeTag);
        renderMainPanel();
        return;
    }

    // Gallery / List item click → detail
    const item = e.target.closest(".gallery-item, .list-row");
    if (item && item.dataset.path) {
        const file = allFiles.find(f => f.path === item.dataset.path);
        if (file) showDetail(file);
        return;
    }

    // View buttons
    const viewBtn = e.target.closest(".view-btn");
    if (viewBtn) { setView(viewBtn.dataset.view); return; }

    // Density buttons
    const densBtn = e.target.closest(".density-btn");
    if (densBtn) {
        currentDensity = densBtn.dataset.density;
        document.querySelectorAll(".density-btn").forEach(b => b.classList.remove("active"));
        densBtn.classList.add("active");
        const root = document.documentElement;
        const sizes = { compact: ["80px", "2rem", "0.7rem"], comfortable: ["120px", "3rem", "0.85rem"], spacious: ["180px", "4.5rem", "1rem"] };
        const s = sizes[currentDensity];
        root.style.setProperty("--gallery-item-size", s[0]);
        root.style.setProperty("--gallery-icon-size", s[1]);
        root.style.setProperty("--gallery-font-size", s[2]);
        return;
    }

    // Modal close
    if (e.target.closest(".modal-close") || e.target.classList.contains("modal-overlay")) {
        document.getElementById("detailModal").style.display = "none";
        return;
    }
});

// Clear filters
document.getElementById("btnClearFilters").addEventListener("click", clearAllFilters);

// Search
document.getElementById("searchInput").addEventListener("input", (e) => {
    const query = e.target.value.trim().toLowerCase();

    if (!query) {
        activeTagFilters = [];
        renderMainPanel();
        return;
    }

    // Parse "+tag1 +tag2" syntax
    const tagMatches = query.match(/\+(\S+)/g);
    if (tagMatches) {
        activeTagFilters = tagMatches.map(m => m.slice(1));
        renderMainPanel();
        return;
    }

    // Fuzzy search by name
    const results = allFiles.filter(f => f.name.toLowerCase().includes(query) || (f.tags || []).some(t => t.includes(query)));
    const container = document.getElementById("contentPreview");
    renderActiveFilters();
    document.getElementById("activeFilters").innerHTML = `<span class="filter-label">${results.length} resultados para "${query}"</span>`;

    if (currentView === "gallery") {
        renderGallery(container, results);
    } else {
        renderList(container, results);
    }
});

// Keyboard shortcut: "/" to focus search
document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement.tagName !== "INPUT") {
        e.preventDefault();
        document.getElementById("searchInput").focus();
    }
    if (e.key === "Escape") {
        document.getElementById("detailModal").style.display = "none";
    }
});

// ============================================================================
// INITIALIZATION
// ============================================================================

async function loadData() {
    try {
        const [enrichedResp, vocabResp] = await Promise.all([
            fetch("dados_enriquecidos.json"),
            fetch("vocabulario.json")
        ]);

        if (!enrichedResp.ok) throw new Error("dados_enriquecidos.json não encontrado.");

        enrichedData = await enrichedResp.json();
        if (vocabResp.ok) vocabulario = await vocabResp.json();

        // Flatten tree into searchable array
        allFiles = flattenTree(enrichedData);

        document.getElementById("totalItems").textContent = allFiles.length.toLocaleString();

        // Render
        renderFacets();
        renderMainPanel();

    } catch (error) {
        document.getElementById("contentPreview").innerHTML = `
            <div class="empty-state" style="color:#ff5858;">
                <div class="empty-icon">⚠️</div>
                <h3>Erro ao carregar dados</h3>
                <p>${error.message}</p>
                <p>Execute <code>uv run python ontologia.py</code> primeiro.</p>
            </div>`;
    }
}

document.addEventListener("DOMContentLoaded", loadData);
