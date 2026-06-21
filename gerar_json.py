import os
import json
import traceback

def get_directory_tree(path):
    name = os.path.basename(path.rstrip(os.sep))
    if not name:
        name = path
        
    tree = {
        "name": name,
        "type": "folder",
        "children": []
    }
    
    try:
        with os.scandir(path) as entries:
            items = list(entries)
    except (PermissionError, FileNotFoundError):
        return tree
        
    try:
        items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
    except Exception:
        items.sort(key=lambda x: x.name.lower())
        
    for item in items:
        try:
            is_dir = item.is_dir()
        except Exception:
            continue
            
        if is_dir:
            tree["children"].append(get_directory_tree(item.path))
        else:
            tree["children"].append({
                "name": item.name,
                "type": "file"
            })
            
    return tree

def main():
    caminho = r"G:\Meu Drive\ORGANIZAR ESSA BOMBA"
    
    if not os.path.exists(caminho):
        print(f"Aviso: O caminho '{caminho}' não foi encontrado.")
        caminho = os.path.dirname(os.path.abspath(__file__))
        print(f"Usando {caminho} como fallback.")
        
    print(f"Gerando JSON a partir de: {caminho}")
    tree_data = get_directory_tree(caminho)
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tree_data, f, ensure_ascii=False, indent=2)
        
    print(f"Dados salvos com sucesso em: {output_path}")

if __name__ == "__main__":
    main()
