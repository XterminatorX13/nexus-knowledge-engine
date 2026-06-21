# Nexus Knowledge Engine — Tasks

## Fase 1: Bottom-Up — Motor de Ontologia (Python)
- [x] Criar `ontologia.py` com extração de entidades
  - [x] Regex para ferramentas/plataformas (shopify, pixai, grok, obsidian...)
  - [x] Regex para datas (2024, 03-2026, etc)
  - [x] Classificador de tipo semântico (captura, recording, manifest, logo...)
  - [x] Classificador de formato (imagem, documento, código, áudio, vídeo)
- [x] Construir Tesauro automático (vocabulario.json)
  - [x] Equivalências (sinônimos)
  - [x] Hierarquias (categorias pai/filho)
  - [x] Associações (termos relacionados)
- [x] Aplicar Facetas PMEST (Ranganathan) a cada arquivo

## Fase 2: Enriquecimento dos Dados
- [x] Gerar `dados_enriquecidos.json` com metadados facetados em cada nó
- [x] Gerar Smart Collections automáticas

## Fase 3: Interface Facetada (Frontend)
- [x] Reescrever `index.html` com painel de facetas e nuvem de tags
- [x] Reescrever `style.css` com estilos para facetas, tags, modal, tesauro
- [x] Reescrever `app.js` para carregar dados enriquecidos e busca facetada
- [x] Implementar busca por interseção de facetas (+tag1 +tag2)
- [x] Modal de detalhe com lookup do Tesauro
- [x] Grafo D3 reagrupado por tags em vez de pastas
