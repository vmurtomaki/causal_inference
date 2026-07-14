# Define the root and the scripts subfolder
$RootDir = Get-Item .
$ScriptsDir = Join-Path $RootDir.FullName "scripts"
$OutputFile = Join-Path $ScriptsDir "project_structure.txt"

# Ensure the scripts directory exists
if (-not (Test-Path $ScriptsDir)) {
    New-Item -ItemType Directory -Path $ScriptsDir | Out-Null
}

$Output = [System.Text.StringBuilder]::new()

# Wrap tree in an XML tag
[void]$Output.AppendLine("<project_tree>")
[void]$Output.AppendLine($RootDir.Name)

$Script:FilesToInclude = [System.Collections.Generic.List[System.IO.FileInfo]]::new()

function ShouldIncludeContent($File) {
    $ExcludeExtensions = @('.csv', '.xlsx', '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.tar', '.gz', '.lock', '.gitkeep')
    $ExcludeNames = @('Makefile', '.env', '.gitignore', '.python-version', 'project_structure.txt', 'CopyProjectStructure.ps1')

    if ($File.Extension -in $ExcludeExtensions) { return $false }
    if ($File.Name -in $ExcludeNames) { return $false }

    return $true
}

function Get-Tree($CurrentDir, $Indent) {
    $ExcludeList = @('.git', '.venv', 'venv', '.mypy_cache', '.pytest_cache', '.ruff_cache', '__pycache__')

    $Dirs = Get-ChildItem -Path $CurrentDir.FullName -Directory | 
            Where-Object { $_.Name -notin $ExcludeList }
    
    $Files = Get-ChildItem -Path $CurrentDir.FullName -File

    # Process Directories
    for ($i = 0; $i -lt $Dirs.Count; $i++) {
        $IsLast = ($i -eq $Dirs.Count - 1) -and ($Files.Count -eq 0)
        $Marker = if ($IsLast) { "└── " } else { "├── " }
        [void]$Output.AppendLine(($Indent + $Marker + $Dirs[$i].Name))
        
        $NextIndent = if ($IsLast) { $Indent + "    " } else { $Indent + "│   " }
        Get-Tree $Dirs[$i] $NextIndent
    }

    # Process Files
    for ($i = 0; $i -lt $Files.Count; $i++) {
        $IsLast = $i -eq ($Files.Count - 1)
        $Marker = if ($IsLast) { "└── " } else { "├── " }
        [void]$Output.AppendLine(($Indent + $Marker + $Files[$i].Name))

        if (ShouldIncludeContent $Files[$i]) {
            $Script:FilesToInclude.Add($Files[$i])
        }
    }
}

# Run tree generator
Get-Tree $RootDir ""
[void]$Output.AppendLine("</project_tree>")

# Append file contents using token-efficient XML tags
foreach ($File in $Script:FilesToInclude) {
    $RelativePath = $File.FullName.Replace($RootDir.FullName, "").TrimStart("\").TrimStart("/")
    $RelativePath = $RelativePath.Replace("\", "/") # Normalize slashes for consistency
    
    [void]$Output.AppendLine("<file path=`"$RelativePath`">")
    
    try {
        # Read file, trim leading/trailing whitespace to save tokens
        $Content = (Get-Content -Path $File.FullName -Raw -Encoding UTF8).Trim()
        [void]$Output.AppendLine($Content)
    } catch {
        [void]$Output.AppendLine("[error reading file]")
    }
    
    [void]$Output.AppendLine("</file>")
}

# Convert and save
$FinalString = $Output.ToString()
$FinalString | Out-File -FilePath $OutputFile -Encoding utf8
$FinalString | Set-Clipboard

Write-Host "Token-efficient structure and contents copied to clipboard and saved!" -ForegroundColor Green