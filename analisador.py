import json
import os
from collections import Counter
import re

with open('dados.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def analyze_node(node, depth=0):
    stats = {'files': 0, 'folders': 0, 'keywords': Counter()}
    if node['type'] == 'folder':
        stats['folders'] += 1
        if 'children' in node:
            for child in node['children']:
                child_stats = analyze_node(child, depth + 1)
                stats['files'] += child_stats['files']
                stats['folders'] += child_stats['folders']
                stats['keywords'].update(child_stats['keywords'])
    else:
        stats['files'] += 1
        # Extract keywords from filename (ignore extension)
        name = os.path.splitext(node['name'])[0]
        words = re.findall(r'[a-zA-Záéíóúâêîôûãõç]{4,}', name.lower())
        # Filter common stop words
        stopwords = {'cópia', 'para', 'como', 'documento', 'título', 'nova', 'final', 'print', 'imagem', 'video', 'foto'}
        words = [w for w in words if w not in stopwords]
        stats['keywords'].update(words)
        
    return stats

print('--- ANÁLISE DE TAXONOMIA ---')
root_files = 0
if 'children' in data:
    for child in data['children']:
        if child['type'] == 'folder':
            stats = analyze_node(child)
            print(f"\\nPASTA RAIZ: {child['name']}")
            print(f"  -> Total Arquivos: {stats['files']}")
            print(f"  -> Total Subpastas: {stats['folders']}")
            top_words = [w[0] for w in stats['keywords'].most_common(8)]
            print(f"  -> Palavras-chave Comuns: {', '.join(top_words)}")
        else:
            root_files += 1

print(f"\nArquivos soltos na raiz: {root_files}")
