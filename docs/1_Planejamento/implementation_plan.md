# Nexus Knowledge Engine — Ontologia e Classificação Facetada

## Fundamento Teórico

A construção do sistema seguirá o modelo híbrido de classificação:

- **Bottom-Up (Warrant Literária)**: Extraímos entidades, padrões e relações diretamente dos ~2.000+ arquivos reais do seu Drive. Os dados ditam as categorias — não o contrário.
- **Top-Down (Warrant Estrutural)**: Aplicamos a sua estrutura existente (`00_INBOX`, `10_BUSINESS`, etc.) como esqueleto taxonômico de primeiro nível, e sobrepomos facetas formais derivadas da teoria de Ranganathan (PMEST).

O resultado final é um sistema de **Classificação Facetada** onde cada arquivo recebe metadados em múltiplos eixos independentes, permitindo navegação não-linear.

---

## Arquitetura do Sistema de Conhecimento

```
dados.json (raw)
     │
     ▼
┌─────────────┐
│ ontologia.py │ ◄── Bottom-up: Extrai entidades dos nomes
│              │ ◄── Top-down: Aplica facetas PMEST
└─────┬───────┘
      │
      ▼
┌──────────────────────┐
│ vocabulario.json     │  ← Vocabulário Controlado + Tesauro
│  - termos canônicos  │     (equivalências, hierarquias,
│  - sinônimos         │      associações)
│  - relações BT/NT/RT │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ dados_enriquecidos.json │ ← Cada arquivo agora tem:
│  - tags[]               │    facetas, entidades, tipo
│  - facets{}             │    semântico, status
│  - relations[]          │
└──────────┬──────────────┘
           │
           ▼
    ┌──────────────┐
    │   app.js     │ ← UI com busca facetada,
    │   (Frontend) │   nuvem de tags, filtros
    └──────────────┘
```

---

## Fase 1: Bottom-Up — Extração e Descoberta (Python)

### [NEW] `ontologia.py`
Script que varre `dados.json` e executa:

1. **Extração de Entidades** — Regex + heurísticas sobre nomes de arquivos:
   - Ferramentas/Plataformas: `shopify`, `pixai`, `grok`, `chatgpt`, `obsidian`
   - Datas: padrões `2024`, `03-2026`, `_v2`
   - Idioma: detecção PT-BR vs EN
   - Tipo Semântico: `captura de tela`, `recording`, `manifest`, `logo`

2. **Construção do Tesauro** — Relações entre termos:
   - **USE/UF (Equivalência)**: `foto` USE `imagem`; `loja` USE `e-commerce`
   - **BT/NT (Hierarquia)**: `IA Generativa` BT `pixai`, `grok`, `chatgpt`
   - **RT (Associação)**: `dropshipping` RT `shopify` RT `produtos`

3. **Frequência e Clusters** — Agrupar termos por co-ocorrência para descobrir "assuntos naturais" que emergem dos dados.

### [NEW] `vocabulario.json`
Saída estruturada do Tesauro:
```json
{
  "termos": {
    "ia-generativa": {
      "label": "IA Generativa",
      "NT": ["pixai", "grok", "chatgpt", "dalle"],
      "RT": ["asset-visual", "prompt"],
      "UF": ["inteligência artificial", "ai-gen"]
    },
    "e-commerce": {
      "label": "E-commerce",
      "NT": ["shopify", "dropshipping"],
      "RT": ["produtos", "vestidos", "luminárias"],
      "UF": ["loja", "loja-virtual"]
    }
  }
}
```

---

## Fase 2: Top-Down — Facetas Formais (Ranganathan PMEST)

Aplicaremos as 5 facetas fundamentais de Ranganathan adaptadas:

| Faceta | Descrição | Exemplo do seu Drive |
|--------|-----------|---------------------|
| **P**ersonality (Domínio) | O assunto principal | `business`, `study`, `games` |
| **M**atter (Formato) | A forma do recurso | `imagem`, `documento`, `código`, `áudio` |
| **E**nergy (Ação/Status) | O que fazer com isso | `ativo`, `referência`, `arquivado`, `rascunho` |
| **S**pace (Origem/Ferramenta) | De onde veio | `shopify`, `pixai`, `obsidian`, `google-takeout` |
| **T**ime (Temporalidade) | Quando foi criado/relevante | `2024`, `2025`, `2026` |

Cada arquivo no `dados_enriquecidos.json` receberá estas 5 facetas automaticamente.

---

## Fase 3: Enriquecimento do JSON

### [NEW] `dados_enriquecidos.json`
Cada nó do arquivo original ganha metadados:
```json
{
  "name": "Captura de tela 2024-05-12 vestido luminária.png",
  "type": "file",
  "facets": {
    "personality": ["business", "e-commerce"],
    "matter": ["imagem", "captura-de-tela"],
    "energy": ["referência"],
    "space": ["shopify"],
    "time": ["2024"]
  },
  "tags": ["vestido", "luminária", "captura-de-tela", "e-commerce"],
  "path": "10_BUSINESS/Produtos/Captura de tela 2024-05-12..."
}
```

---

## Fase 4: Interface — Busca Facetada e Navegação Semântica

### [MODIFY] `app.js` e `index.html`
- Substituir a navegação por pastas no painel principal por **Painéis de Facetas**.
- Barra lateral esquerda: Facetas clicáveis (Domínio, Formato, Ferramenta, Ano).
- Cada clique numa faceta filtra os resultados instantaneamente (interseção).
- Campo de busca avançada: `+business +imagem +2024` → retorna tudo que bate.
- Nuvem de Tags dinâmica mostrando os termos mais frequentes do contexto atual.

---

## Verificação

1. Rodar `ontologia.py` e validar que o `vocabulario.json` gerado faz sentido semântico.
2. Rodar o enriquecimento e verificar que `dados_enriquecidos.json` tem facetas em todos os nós.
3. Carregar no navegador e testar a busca facetada cruzando múltiplos eixos.

> [!IMPORTANT]
> **Decisão necessária:** O Tesauro (relações USE/BT/NT/RT) precisa de uma base inicial de regras que eu vou criar baseado nos padrões que já descobri nos seus dados. Conforme você usa o sistema, ele pode ser refinado manualmente. Você concorda com essa abordagem de "seed automático + refinamento humano"?
