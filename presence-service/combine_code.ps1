<#
.SYNOPSIS
Объединяет все Python-файлы в проекте
#>

# Настройки
$outputFile = "all_code.txt"
$excludeDirs = @("venv", ".venv", "__pycache__", ".git", ".idea", "env", "alembic")

# Создаем выходной файл
"=== PYTHON CODE COLLECTION ===" | Out-File -FilePath $outputFile -Encoding utf8
"Generated: $(Get-Date)`n" | Out-File -FilePath $outputFile -Append -Encoding utf8

# Получаем все .py файлы
$pyFiles = Get-ChildItem -Recurse -File -Filter "*.py" | 
    Where-Object {
        $exclude = $false
        foreach ($dir in $excludeDirs) {
            if ($_.FullName -match [regex]::Escape($dir)) {
                $exclude = $true
                break
            }
        }
        -not $exclude
    }

# Добавляем структуру
"`n=== FILE STRUCTURE ===" | Out-File -FilePath $outputFile -Append -Encoding utf8
$pyFiles | ForEach-Object {
    "  $($_.FullName.Substring($pwd.Path.Length + 1))"
} | Out-File -FilePath $outputFile -Append -Encoding utf8

# Добавляем содержимое
"`n`n=== FILE CONTENTS ===" | Out-File -FilePath $outputFile -Append -Encoding utf8

foreach ($file in $pyFiles) {
    $relativePath = $file.FullName.Substring($pwd.Path.Length + 1)
    
    # Заголовок файла
    "`n`n===== FILE: $relativePath =====" | Out-File -FilePath $outputFile -Append -Encoding utf8
    
    # Содержимое с обработкой кодировки
    try {
        $content = Get-Content -Path $file.FullName -Raw -Encoding utf8 -ErrorAction Stop
    }
    catch {
        try {
            $content = [System.IO.File]::ReadAllText($file.FullName)
        }
        catch {
            $content = "!!! COULD NOT READ FILE !!!"
        }
    }
    
    $content | Out-File -FilePath $outputFile -Append -Encoding utf8
    "`n===== END OF FILE =====" | Out-File -FilePath $outputFile -Append -Encoding utf8
}

Write-Host "Done! All Python files combined in $outputFile"
