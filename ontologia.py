#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nexus Knowledge Engine — ontologia.py
Motor de Classificação Facetada baseado em Ciência da Informação.

Abordagem Híbrida:
  - Bottom-Up: Extrai entidades, padrões e clusters dos nomes reais dos arquivos.
  - Top-Down: Aplica Facetas PMEST (Ranganathan) e Vocabulário Controlado.

Saídas:
  - vocabulario.json   → Tesauro com relações de equivalência, hierarquia e associação
  - dados_enriquecidos.json → Cada arquivo com facetas e tags automáticas
"""

import json
import os
import re
import sys
from collections import Counter, defaultdict

# ============================================================================
# FASE TOP-DOWN: Vocabulário Controlado (definido manualmente + dados)
# ============================================================================

# Relações do Tesauro:
#   "label"    → Nome canônico do termo (human-readable)
#   "sinonimos" (UF/USE) → Termos equivalentes que apontam para este
#   "categoria_pai" (BT) → Termo mais amplo / generalização
#   "subcategorias" (NT) → Termos mais específicos
#   "relacionados" (RT) → Termos associados semanticamente

TESAURO_SEED = {
    # --- DOMÍNIOS (Personality) ---
    "business": {
        "label": "Negócios",
        "sinonimos": ["negócio", "empresa", "comercial", "empreendimento"],
        "subcategorias": ["e-commerce", "marketing", "branding", "administrativo"],
        "relacionados": ["estudo", "finanças"]
    },
    "e-commerce": {
        "label": "E-commerce",
        "sinonimos": ["loja", "loja-virtual", "loja-online", "shop"],
        "categoria_pai": "business",
        "subcategorias": ["shopify", "dropshipping", "dsers"],
        "relacionados": ["produtos", "marketing", "precificação"]
    },
    "estudo": {
        "label": "Estudo",
        "sinonimos": ["study", "aprendizado", "curso", "tutorial"],
        "subcategorias": ["dropshipping", "programação", "concurso"],
        "relacionados": ["business"]
    },
    "pessoal": {
        "label": "Pessoal",
        "sinonimos": ["personal", "privado"],
        "subcategorias": ["saúde", "finanças-pessoais", "documentos-pessoais"],
        "relacionados": []
    },
    "criativo": {
        "label": "Criativo",
        "sinonimos": ["creative", "arte", "design"],
        "subcategorias": ["ia-generativa", "fotografia", "edição"],
        "relacionados": ["branding", "games"]
    },
    "games": {
        "label": "Games & Entretenimento",
        "sinonimos": ["jogos", "entretenimento", "gaming"],
        "subcategorias": ["ia-generativa"],
        "relacionados": ["criativo"]
    },

    # --- FERRAMENTAS / PLATAFORMAS (Space) ---
    "shopify": {
        "label": "Shopify",
        "sinonimos": ["shopify-store"],
        "categoria_pai": "e-commerce",
        "relacionados": ["dsers", "dropshipping", "produtos"]
    },
    "dropshipping": {
        "label": "Dropshipping",
        "sinonimos": ["drop", "dsers"],
        "categoria_pai": "e-commerce",
        "relacionados": ["shopify", "produtos", "fornecedores"]
    },
    "obsidian": {
        "label": "Obsidian",
        "sinonimos": ["vault", "obsidian-vault"],
        "categoria_pai": "ferramentas",
        "relacionados": ["notas", "markdown", "plugins"]
    },
    "ia-generativa": {
        "label": "IA Generativa",
        "sinonimos": ["ai-gen", "inteligência-artificial", "geração-ia"],
        "subcategorias": ["pixai", "grok", "chatgpt", "dalle", "midjourney"],
        "relacionados": ["criativo", "asset-visual", "prompt"]
    },
    "pixai": {
        "label": "PixAI",
        "sinonimos": ["pix-ai"],
        "categoria_pai": "ia-generativa",
        "relacionados": ["asset-visual", "anime"]
    },
    "grok": {
        "label": "Grok (xAI)",
        "sinonimos": [],
        "categoria_pai": "ia-generativa",
        "relacionados": ["asset-visual"]
    },
    "chatgpt": {
        "label": "ChatGPT",
        "sinonimos": ["openai", "gpt"],
        "categoria_pai": "ia-generativa",
        "relacionados": ["prompt", "texto"]
    },
    "google": {
        "label": "Google",
        "sinonimos": ["gsheet", "gdoc", "google-drive", "takeout"],
        "subcategorias": ["google-sheets", "google-docs"],
        "relacionados": ["produtividade"]
    },

    # --- TIPOS SEMÂNTICOS (Matter) ---
    "asset-visual": {
        "label": "Ativo Visual",
        "sinonimos": ["imagem", "foto", "visual", "gráfico"],
        "subcategorias": ["logo", "banner", "background", "screenshot", "foto-produto"],
        "relacionados": ["branding", "e-commerce"]
    },
    "logo": {
        "label": "Logotipo",
        "sinonimos": ["logotype", "logomarca", "marca"],
        "categoria_pai": "asset-visual",
        "relacionados": ["branding", "identidade-visual"]
    },
    "banner": {
        "label": "Banner",
        "sinonimos": [],
        "categoria_pai": "asset-visual",
        "relacionados": ["marketing", "campanha"]
    },
    "screenshot": {
        "label": "Captura de Tela",
        "sinonimos": ["captura", "screencapture", "print", "printscreen"],
        "categoria_pai": "asset-visual",
        "relacionados": ["referência"]
    },
    "documento": {
        "label": "Documento",
        "sinonimos": ["doc", "texto", "relatório", "planilha"],
        "subcategorias": ["contrato", "planilha", "apresentação", "guia"],
        "relacionados": ["produtividade"]
    },
    "codigo": {
        "label": "Código-Fonte",
        "sinonimos": ["code", "script", "programa", "source"],
        "subcategorias": ["manifest", "styles", "config", "plugin"],
        "relacionados": ["programação", "obsidian"]
    },
    "audio": {
        "label": "Áudio",
        "sinonimos": ["som", "gravação", "podcast"],
        "subcategorias": ["recording"],
        "relacionados": ["imersão"]
    },

    # --- BRANDING / PROJETOS (Entities) ---
    "beriam": {
        "label": "BERIAM",
        "sinonimos": ["beriam-store", "beriam.com"],
        "categoria_pai": "e-commerce",
        "subcategorias": ["beriam-produtos", "beriam-idv", "beriam-campanhas"],
        "relacionados": ["shopify", "moda", "decoração"]
    },
    "moda": {
        "label": "Moda",
        "sinonimos": ["fashion", "roupa", "vestuário", "clothing"],
        "subcategorias": ["vestido", "calça", "blazer", "jaqueta", "camisa", "cinto", "bolsa"],
        "relacionados": ["beriam", "e-commerce"]
    },
    "decoracao": {
        "label": "Decoração",
        "sinonimos": ["decoração", "casa", "cozinha", "home", "lar", "móveis"],
        "subcategorias": ["luminária", "pendente", "mesa"],
        "relacionados": ["beriam", "e-commerce"]
    },

    # --- STATUS (Energy) ---
    "campanha": {
        "label": "Campanha Sazonal",
        "sinonimos": ["sazonal", "promoção"],
        "subcategorias": ["black-friday", "natal", "dia-das-mães", "carnaval"],
        "relacionados": ["marketing", "e-commerce"]
    }
}


# ============================================================================
# FASE BOTTOM-UP: Regras de Extração de Entidades
# ============================================================================

# Mapeamento extensão → tipo semântico (Matter facet)
EXT_TO_MATTER = {
    # Imagens
    ".png": "imagem", ".jpg": "imagem", ".jpeg": "imagem",
    ".svg": "imagem", ".webp": "imagem", ".gif": "imagem",
    ".ico": "imagem", ".bmp": "imagem",
    # Documentos
    ".pdf": "documento", ".doc": "documento", ".docx": "documento",
    ".gdoc": "documento", ".txt": "documento", ".md": "documento",
    # Planilhas
    ".xlsx": "planilha", ".csv": "planilha", ".gsheet": "planilha",
    # Vídeo
    ".mp4": "video", ".mov": "video", ".avi": "video", ".mkv": "video",
    # Áudio
    ".m4a": "audio", ".mp3": "audio", ".wav": "audio", ".ogg": "audio",
    # Código
    ".js": "codigo", ".css": "codigo", ".html": "codigo",
    ".py": "codigo", ".json": "codigo", ".ini": "codigo",
    ".xml": "codigo", ".yaml": "codigo", ".yml": "codigo",
    # Compactados
    ".zip": "compactado", ".rar": "compactado", ".7z": "compactado",
    ".tar": "compactado", ".gz": "compactado",
    # Links
    ".lnk": "atalho", ".url": "atalho",
    # Outros
    ".ttf": "fonte", ".otf": "fonte", ".woff": "fonte", ".woff2": "fonte",
}

# Padrões regex para detectar entidades nos nomes de arquivos e pastas
ENTITY_PATTERNS = [
    # Ferramentas / Plataformas
    (r'\bshopify\b', 'shopify'),
    (r'\bdsers?\b', 'dropshipping'),
    (r'\bdropship(?:ping)?\b', 'dropshipping'),
    (r'\bpixai\b', 'pixai'),
    (r'\bgrok\b', 'grok'),
    (r'\bchatgpt\b', 'chatgpt'),
    (r'\bdall[·\-]?e\b', 'ia-generativa'),
    (r'\bmidjourney\b', 'ia-generativa'),
    (r'\bobsidian\b', 'obsidian'),
    (r'\bgoogle\b', 'google'),
    (r'\bhubspot\b', 'marketing'),
    (r'\bfacebook\b', 'marketing'),
    (r'\binstagram\b', 'marketing'),

    # Tipos semânticos
    (r'\blogo(?:tipo|type|marca)?\b', 'logo'),
    (r'\bbanner\b', 'banner'),
    (r'\bbackground\b', 'background'),
    (r'\bscreen(?:capture|shot)\b', 'screenshot'),
    (r'\bcaptura\s*(?:de\s*)?tela\b', 'screenshot'),
    (r'\brecording\b', 'audio'),
    (r'\bmanifest\b', 'codigo'),
    (r'\bstyles?\b', 'codigo'),
    (r'\bplugin\b', 'codigo'),
    (r'\btheme\b', 'codigo'),
    (r'\bconfig\b', 'codigo'),

    # Entidades de negócio
    (r'\bberiam\b', 'beriam'),
    (r'\bvestido\b', 'moda'),
    (r'\bcalça\b', 'moda'),
    (r'\bblazer\b', 'moda'),
    (r'\bjaqueta\b', 'moda'),
    (r'\bcamisa\b', 'moda'),
    (r'\bcinto\b', 'moda'),
    (r'\bbolsa\b', 'moda'),
    (r'\bcasaco\b', 'moda'),
    (r'\bcostume\b', 'moda'),
    (r'\bmochila\b', 'moda'),
    (r'\bluminária\b', 'decoracao'),
    (r'\bpendente\b', 'decoracao'),
    (r'\bdecoraç[aã]o\b', 'decoracao'),
    (r'\bcozinha\b', 'decoracao'),
    (r'\bm[oó]veis?\b', 'decoracao'),

    # Campanhas
    (r'\bblack[\s\-]?friday\b', 'campanha'),
    (r'\bnatal\b', 'campanha'),
    (r'\bpáscoa\b', 'campanha'),
    (r'\bcarnaval\b', 'campanha'),
    (r'\bdia\s+d[aeo]s?\b', 'campanha'),

    # Conceitos de estudo
    (r'\bconcurso\b', 'estudo'),
    (r'\bprecificaç[aã]o\b', 'business'),
    (r'\bmarketing\b', 'marketing'),
    (r'\bprodutos?\b', 'produtos'),
]

# Padrão para extrair datas (Time facet)
DATE_PATTERNS = [
    (r'\b(20[12][0-9])\b', None),           # 2020, 2024, 2025, 2026...
    (r'\b(\d{2})-(\d{4})\b', None),         # 03-2026
    (r'\b(\d{4})-(\d{2})-(\d{2})\b', None), # 2024-05-12
]

# Mapeamento de pastas raiz → Domínio (Personality facet)
ROOT_DOMAIN_MAP = {
    "00_INBOX": "inbox",
    "10_BUSINESS": "business",
    "20_PERSONAL": "pessoal",
    "30_STUDY": "estudo",
    "40_CREATIVE": "criativo",
    "80_GAMES": "games",
    "90_ARCHIVE": "arquivo",
}


# ============================================================================
# MOTOR DE ENRIQUECIMENTO
# ============================================================================

global_tag_counter = Counter()
smart_collections = defaultdict(list)

def extract_extension(name):
    """Retorna a extensão em minúsculo."""
    _, ext = os.path.splitext(name)
    return ext.lower() if ext else ""

def extract_date(text):
    """Extrai ano de um texto."""
    years = re.findall(r'\b(20[12][0-9])\b', text)
    return list(set(years))

def extract_entities(text):
    """Aplica todos os padrões regex e retorna tags encontradas."""
    tags = set()
    lower = text.lower()
    for pattern, tag in ENTITY_PATTERNS:
        if re.search(pattern, lower):
            tags.add(tag)
    return tags

def get_domain_from_path(path_segments):
    """Determina o Domínio (Personality) baseado na pasta raiz."""
    if not path_segments:
        return "indefinido"
    root = path_segments[0]
    return ROOT_DOMAIN_MAP.get(root, "indefinido")

def get_energy(path_segments, node_name):
    """Determina o status/ação (Energy facet)."""
    path_str = "/".join(path_segments).lower()
    name_lower = node_name.lower()

    if "archive" in path_str or "arquivo" in path_str:
        return "arquivado"
    if "inbox" in path_str:
        return "pendente"
    if "rascunho" in name_lower or "draft" in name_lower:
        return "rascunho"
    if any(kw in name_lower for kw in ["inspiração", "referência", "inspiration"]):
        return "referência"
    return "ativo"

def enrich_node(node, path_segments=None):
    """Enriquece um nó com facetas PMEST e tags."""
    if path_segments is None:
        path_segments = []

    is_folder = node["type"] == "folder"
    name = node["name"]
    full_path = "/".join(path_segments + [name])

    # --- Extrair facetas ---
    tags = set()

    # Personality (Domínio)
    personality = get_domain_from_path(path_segments)

    # Matter (Formato)
    if is_folder:
        matter = "pasta"
    else:
        ext = extract_extension(name)
        matter = EXT_TO_MATTER.get(ext, "outro")

    # Energy (Status)
    energy = get_energy(path_segments, name)

    # Space (Ferramenta/Origem) — extraído do nome e caminho
    space_tags = set()
    for seg in path_segments + [name]:
        space_tags.update(extract_entities(seg))

    # Time (Temporalidade)
    time_tags = extract_date(full_path)

    # Adicionar todas as entidades detectadas como tags
    tags.update(space_tags)
    if matter not in ("pasta", "outro"):
        tags.add(matter)
    if personality != "indefinido":
        tags.add(personality)

    # Contexto do caminho das pastas como tags adicionais
    # Filtra ruído técnico e limita aos 3 primeiros segmentos significativos
    NOISE_SEGMENTS = {
        '.git', '.venv', 'venv', 'env', '__pycache__', 'node_modules',
        'site-packages', 'lib', 'lib64', 'objects', 'pack', 'refs',
        'hooks', 'info', 'logs', 'branches', 'tags', 'heads',
        'users', 'appdata', 'roaming', 'local', 'programs',
        'drive-c', 'program files', 'program files (x86)',
        'nova pasta', 'desktop.ini', 'thumbs.db',
        'dist', 'build', 'bin', 'obj', 'target', 'out',
        '.cache', '.config', '.local', '.npm', '.yarn',
        'minecraft_ bedrock edition', 'minecraft bedrock',
        'ludusavi-backup', 'email subs',
        'organizar essa bomba',  # Raiz do drive (não é tag)
        'organização pessoal', 'cloud hub',  # Pastas de agrupamento genérico
        'archive', 'inbox', 'children',
    }
    meaningful_segments = []
    for seg in path_segments[:4]:  # Apenas primeiros 4 níveis
        seg_clean = re.sub(r'^[\d]+[\._\s]*', '', seg)  # Remove números de prefixo
        seg_clean = re.sub(r'[\U0001f000-\U0001ffff]', '', seg_clean).strip()  # Remove emojis
        seg_clean = re.sub(r'[📊🔗📦⚙️💼📸🧑‍💻☁]', '', seg_clean).strip()
        if (seg_clean
            and len(seg_clean) > 2
            and seg_clean.lower() not in NOISE_SEGMENTS
            and not seg_clean.startswith('.')
            and not seg_clean.startswith('__')):
            meaningful_segments.append(seg_clean.lower())
    tags.update(meaningful_segments)

    # Converter para lista ordenada
    tags_list = sorted(list(tags))
    global_tag_counter.update(tags_list)

    # Smart Collections
    if matter == "imagem" and any(t in tags for t in ["pixai", "grok", "chatgpt", "ia-generativa"]):
        smart_collections["gerado-por-ia"].append(full_path)
    if matter in ("imagem",) and "screenshot" in tags:
        smart_collections["screenshots"].append(full_path)
    if energy == "pendente":
        smart_collections["pendentes-inbox"].append(full_path)
    if energy == "arquivado":
        smart_collections["arquivo-morto"].append(full_path)
    if is_folder and (not node.get("children") or len(node.get("children", [])) == 0):
        smart_collections["pastas-vazias"].append(full_path)

    # --- Construir nó enriquecido ---
    enriched = {
        "name": name,
        "type": node["type"],
        "path": full_path,
        "facets": {
            "dominio": personality,
            "formato": matter,
            "status": energy,
            "ferramentas": sorted(list(space_tags)) if space_tags else [],
            "periodo": time_tags if time_tags else []
        },
        "tags": tags_list
    }

    if is_folder and "children" in node:
        enriched["children"] = [
            enrich_node(child, path_segments + [name])
            for child in node["children"]
        ]

    return enriched


# ============================================================================
# EXECUÇÃO
# ============================================================================

def main():
    # Forçar UTF-8 no stdout
    sys.stdout.reconfigure(encoding='utf-8')

    print("=== Nexus Knowledge Engine ===")
    print("Carregando dados.json...")

    with open("dados.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Aplicando ontologia e facetas PMEST...")
    enriched = enrich_node(data)

    # Salvar dados enriquecidos
    with open("dados_enriquecidos.json", "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)
    print(f"  -> dados_enriquecidos.json salvo.")

    # Construir e salvar vocabulário/tesauro
    # Adicionar frequência real das tags ao tesauro
    vocabulario = {
        "meta": {
            "descricao": "Tesauro e Vocabulario Controlado - Nexus Knowledge Engine",
            "legenda": {
                "label": "Nome canônico do termo",
                "sinonimos": "Termos equivalentes (USE/UF) - também conhecido como",
                "categoria_pai": "Termo mais amplo (BT) - pertence a",
                "subcategorias": "Termos mais específicos (NT) - contém",
                "relacionados": "Termos associados (RT) - ver também"
            }
        },
        "termos": TESAURO_SEED,
        "frequencia_tags": dict(global_tag_counter.most_common(50)),
        "smart_collections": {
            k: {"total": len(v), "exemplos": v[:5]}
            for k, v in smart_collections.items()
        }
    }

    with open("vocabulario.json", "w", encoding="utf-8") as f:
        json.dump(vocabulario, f, ensure_ascii=False, indent=2)
    print(f"  -> vocabulario.json salvo.")

    # Resumo
    print(f"\n=== RESUMO ===")
    print(f"Top 20 Tags mais frequentes:")
    for tag, count in global_tag_counter.most_common(20):
        print(f"  {tag}: {count}")
    print(f"\nSmart Collections:")
    for name, items in smart_collections.items():
        print(f"  {name}: {len(items)} itens")
    print(f"\nProcessamento concluído!")


if __name__ == "__main__":
    main()
