# Define the root and the scripts subfolder
$RootDir = Get-Item .
$ScriptsDir = Join-Path $RootDir.FullName "scripts"
$OutputFile = Join-Path $ScriptsDir "project_structure.txt"

# Ensure the scripts directory exists
if (-not (Test-Path $ScriptsDir)) {
    New-Item -ItemType Directory -Path $ScriptsDir | Out-Null
}

$Output = [System.Text.StringBuilder]::new()
[void]$Output.AppendLine($RootDir.Name)

function Get-Tree($CurrentDir, $Indent) {
    # Get directories, excluding .git and .venv
    $Dirs = Get-ChildItem -Path $CurrentDir.FullName -Directory | 
            Where-Object { $_.Name -notin '.git', '.venv' }
    
    # Get files in the current directory
    $Files = Get-ChildItem -Path $CurrentDir.FullName -File

    # Process Directories
    for ($i = 0; $i -lt $Dirs.Count; $i++) {
        $IsLast = ($i -eq $Dirs.Count - 1) -and ($Files.Count -eq 0)
        $Marker = if ($IsLast) { "└── " } else { "├── " }
        [void]$Output.AppendLine(($Indent + $Marker + $Dirs[$i].Name))
        
        # Fixed for PS 5.1 compatibility: Clean if/else blocks for indentation
        if ($IsLast) {
            $NextIndent = $Indent + "    "
        } else {
            $NextIndent = $Indent + "│   "
        }
        
        Get-Tree $Dirs[$i] $NextIndent
    }

    # Process Files
    for ($i = 0; $i -lt $Files.Count; $i++) {
        $IsLast = $i -eq ($Files.Count - 1)
        $Marker = if ($IsLast) { "└── " } else { "├── " }
        [void]$Output.AppendLine(($Indent + $Marker + $Files[$i].Name))
    }
}

# Run the function
Get-Tree $RootDir ""

# Convert to string
$TreeString = $Output.ToString()

# Save the file into the scripts subfolder and copy to clipboard
$TreeString | Out-File -FilePath $OutputFile -Encoding utf8
$TreeString | Set-Clipboard

Write-Host "Folder structure successfully copied to clipboard and saved to scripts/project_structure.txt!" -ForegroundColor Green