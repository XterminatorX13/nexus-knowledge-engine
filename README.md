# 🧠 Nexus Knowledge Engine

Um motor de classificação semântica para estruturação autônoma de arquivos locais, baseado na teoria de Classificação Facetada da Ciência da Informação.

O Nexus Knowledge Engine transforma o caos de diretórios locais não estruturados em uma base de conhecimento rica e mapeada, utilizando uma abordagem híbrida de extração de dados.

## 🚀 Como Funciona

O núcleo lógico reside no `ontologia.py`, que escaneia arquivos e aplica duas camadas de inteligência:

1. **Top-Down (Tesauro Base):** Um vocabulário controlado que compreende hierarquias semânticas (Domínios como *Business*, *Creative*, *Study*). Ele identifica sinônimos e conecta termos relacionados automaticamente.
2. **Bottom-Up (Regex Extraction):** Um parser que lê metadados implícitos nos nomes dos arquivos (ferramentas como *Shopify* ou *Midjourney*, e tipos semânticos como *Logotipos* ou *Banners*).

A interseção dessas duas camadas preenche as Facetas **PMEST** (Personality, Matter, Energy, Space, Time), gerando um `dados_enriquecidos.json` pronto para ser consumido por qualquer interface visual.

## 🌟 Features
- Geração autônoma de **Smart Collections** (ex: *Gerado por IA*, *Pendentes Inbox*).
- Extração de temporalidade e ferramentas ocultas em strings brutas.
- Mapeamento hierárquico persistido em um `vocabulario.json` robusto.
