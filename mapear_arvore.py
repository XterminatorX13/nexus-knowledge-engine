import os
from rich.console import Console
from rich.tree import Tree
from rich.text import Text
from rich.style import Style

# Configuração do console (permite exportar para HTML)
console = Console(record=True)

# Dicionário de ícones estilo Yazi (Emojis universais para garantir renderização)
ICONES = {
    "pasta": "📁",
    "default": "📄",
    ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️", ".svg": "🎨",
    ".xlsx": "📊", ".csv": "📉", ".gsheet": "📊",
    ".pdf": "📕", ".doc": "📝", ".docx": "📝",
    ".mp4": "🎥", ".mov": "🎥",
    ".zip": "📦", ".rar": "📦",
    ".txt": "📜", ".json": "⚙️"
}

def obter_icone(nome_arquivo, e_pasta=False):
    if e_pasta:
        return ICONES["pasta"]
    
    _, ext = os.path.splitext(nome_arquivo)
    return ICONES.get(ext.lower(), ICONES["default"])

def construir_arvore(caminho_diretorio, arvore_pai, max_arquivos_por_pasta=20):
    try:
        # Usa os.scandir que é muito mais rápido em unidades de rede/Google Drive
        with os.scandir(caminho_diretorio) as entries:
            itens = list(entries)
    except (PermissionError, FileNotFoundError):
        return # Pula pastas sem permissão ou inexistentes

    # Ordena: pastas primeiro, depois arquivos
    try:
        itens.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
    except Exception:
        # Fallback de ordenação simples caso ocorra algum erro de I/O ao ler is_dir()
        itens.sort(key=lambda x: x.name.lower())

    arquivos_mostrados = 0
    total_arquivos_na_pasta = 0
    for item in itens:
        try:
            if item.is_file():
                total_arquivos_na_pasta += 1
        except Exception:
            pass

    for item in itens:
        try:
            e_pasta = item.is_dir()
        except Exception:
            continue # Pula arquivos com erro de I/O

        caminho_completo = item.path
        nome_item = item.name
        icone = obter_icone(nome_item, e_pasta)
        
        if e_pasta:
            # Estilo para pastas (Azul e negrito)
            texto_pasta = Text(f"{icone} {nome_item}", style="bold blue")
            ramo = arvore_pai.add(texto_pasta)
            construir_arvore(caminho_completo, ramo, max_arquivos_por_pasta)
        else:
            # Controle de flood no terminal: limita a quantidade de arquivos exibidos por pasta
            if arquivos_mostrados < max_arquivos_por_pasta:
                # Estilo para arquivos (Cinza claro)
                texto_arquivo = Text(f"{icone} {nome_item}", style="dim white")
                arvore_pai.add(texto_arquivo)
                arquivos_mostrados += 1
            
    # Se houver mais arquivos do que o limite, adiciona um aviso visual
    arquivos_ocultos = total_arquivos_na_pasta - max_arquivos_por_pasta
    if arquivos_ocultos > 0:
        arvore_pai.add(Text(f"↪ ... e mais {arquivos_ocultos} arquivos", style="italic red"))

def mapear_arvore_visual(caminho_base):
    console.print(f"\n[bold yellow]Construindo árvore de diretórios a partir de:[/bold yellow] [bold green]{caminho_base}[/bold green]\n")
    
    nome_raiz = os.path.basename(caminho_base.rstrip(os.sep))
    if not nome_raiz:
        nome_raiz = caminho_base
    texto_raiz = Text(f"🗄️ {nome_raiz}", style="bold magenta")
    arvore_principal = Tree(texto_raiz, guide_style="bold bright_black")
    
    # Você pode alterar o max_arquivos_por_pasta se quiser ver TUDO (coloque 99999)
    construir_arvore(caminho_base, arvore_principal, max_arquivos_por_pasta=15)
    
    # Imprime no terminal
    console.print(arvore_principal)
    
    # Exporta o exato visual do terminal para um HTML
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arvore_yazi.html")
    console.save_html(html_path)
    console.print(f"\n[bold green]✅ Árvore completa salva como '{html_path}'.[/bold green] [dim]Abra no navegador para visualizar sem lag.[/dim]")

if __name__ == "__main__":
    # Caminho do seu Drive
    caminho_do_problema = r"G:\Meu Drive\ORGANIZAR ESSA BOMBA"
    if not os.path.exists(caminho_do_problema):
        # Fallback local para teste caso o drive não esteja montado
        print(f"Aviso: O caminho '{caminho_do_problema}' não foi encontrado. Tentando mapear a pasta scratch como exemplo...")
        caminho_do_problema = os.path.dirname(os.path.abspath(__file__))
    mapear_arvore_visual(caminho_do_problema)
