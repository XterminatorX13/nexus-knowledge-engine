$ErrorActionPreference = "Stop"

# Caminhos
$BaseDir = "G:\Meu Drive\ORGANIZAR ESSA BOMBA"
$HtmlTemplatePath = "C:\Users\Victor\.gemini\antigravity-ide\scratch\organizer_template4.html"
$HtmlOutputPath = "C:\Users\Victor\.gemini\antigravity-ide\scratch\organizer_active.html"

Write-Host "Lendo arquivos e pastas em: $BaseDir..." -ForegroundColor Cyan

# Pega apenas arquivos soltos na raiz (ignora pastas)
$LooseFiles = Get-ChildItem -Path $BaseDir -File
# Pega todas as pastas recursivamente
$AllFolders = Get-ChildItem -Path $BaseDir -Directory -Recurse

# Prepara a lista de arquivos
$FilesData = @()
foreach ($file in $LooseFiles) {
    $FilesData += @{
        name = $file.Name
        path = $file.FullName
        fullPath = $file.FullName
        isFolder = $false
    }
}

# (Opcional) Podemos incluir pastas da raiz que você queira organizar como se fossem "arquivos"
# Por exemplo, pastas soltas que não são as suas categorias principais
$RootDirs = Get-ChildItem -Path $BaseDir -Directory
foreach ($dir in $RootDirs) {
    # Ignora as categorias principais para não aparecerem como itens soltos a organizar
    if ($dir.Name -notmatch "^(00|10|20|30|40|80|90|WORK|Obsidian)") {
        $FilesData += @{
            name = $dir.Name
            path = $dir.FullName
            fullPath = $dir.FullName
            isFolder = $true
        }
    }
}

# Prepara a lista de pastas destino
$FoldersData = @()
foreach ($folder in $AllFolders) {
    # Remove o caminho base para ficar apenas o caminho relativo (ex: 10_BUSINESS\Ativos)
    $relativePath = $folder.FullName.Substring($BaseDir.Length + 1)
    $FoldersData += $relativePath
}

# Se não tiver nenhuma subpasta, colocamos as raízes principais também
foreach ($dir in $RootDirs) {
    if ($dir.Name -match "^(00|10|20|30|40|80|90|WORK|Obsidian)") {
        $FoldersData += $dir.Name
    }
}
$FoldersData = $FoldersData | Select-Object -Unique

# Monta o JSON
$JsonData = @{
    files = $FilesData
    folders = $FoldersData
} | ConvertTo-Json -Depth 10 -Compress

# Lê o HTML Template
$HtmlContent = Get-Content -Path $HtmlTemplatePath -Raw

# Substitui o placeholder com os dados reais
$Pattern = '(?s)/\*DATA_PLACEHOLDER\*/.*?/\*END_PLACEHOLDER\*/'
$Replacement = $JsonData
$NewHtmlContent = $HtmlContent -replace $Pattern, $Replacement

# Salva o novo HTML
Set-Content -Path $HtmlOutputPath -Value $NewHtmlContent -Encoding UTF8

Write-Host "Organizador gerado com sucesso! Abrindo no navegador..." -ForegroundColor Green
Invoke-Item $HtmlOutputPath
