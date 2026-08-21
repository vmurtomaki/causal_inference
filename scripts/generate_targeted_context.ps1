<#
.SYNOPSIS
    Gathers a compact project tree, prioritized codebase files, data schemas, 
    and artifact examples for the Causal Pricing Engine into a single .txt file
    for Gemini Notebook / NotebookLM ingestion, and copies it to clipboard.

.DESCRIPTION
    Ordered context included:
      1. Project directory tree
      2. High-level documentation & dev standards (README.md, DEVELOPER_INSTRUCTION.md)
      3. Environment & config (pyproject.toml, config.py)
      4. Observational data schema & artifact contracts
      5. Core mathematical engine (data_ingestion.py, dml_engine.py, artifact_manager.py)
      6. Execution entrypoints & UI (main.py, app.py)
      7. Mathematical fixtures & tests (test_dml_recovery.py, unit tests)
      8. CI/CD & orchestration (Makefile, ci.yml)
#>

[CmdletBinding()]
param(
    [string]$OutputPath = ""
)

$repoRoot = if (Test-Path "$PSScriptRoot/../src") {
    (Resolve-Path "$PSScriptRoot/..").Path
} else {
    $PWD.Path
}

if (-not $OutputPath) {
    $OutputPath = Join-Path $repoRoot "scripts/llm_context.txt"
}

$sb = [System.Text.StringBuilder]::new()

function Append-Block {
    param (
        [string]$Tag,
        [string]$Attributes = "",
        [string]$Content
    )
    $attrStr = if ($Attributes) { " $Attributes" } else { "" }
    [void]$sb.AppendLine("<$Tag$attrStr>")
    [void]$sb.AppendLine($Content.Trim())
    [void]$sb.AppendLine("</$Tag>")
    [void]$sb.AppendLine()
}

# ----------------------------------------------------------------------
# 1. Token-Efficient Project Structure
# ----------------------------------------------------------------------
function Get-CompactProjectTree {
    param ([string]$Root)

    $ignoreDirs = @(
        '.git', '.pytest_cache', '.ruff_cache', '__pycache__',
        '.venv', 'venv', '.mypy_cache', 'docs'
    )
    $ignoreFiles = @(
        '*.pyc', 'CACHEDIR.TAG', '.DS_Store', 'llm_context.txt',
        'uv.lock', '*.png', '*.jpg', '*.jpeg'
    )

    $items = Get-ChildItem -Path $Root -Recurse -Force | Where-Object {
        $rel = $_.FullName.Substring($Root.Length).TrimStart('\', '/')
        $parts = $rel -split '[\\/]'
        
        foreach ($d in $ignoreDirs) {
            if ($parts -contains $d) { return $false }
        }
        foreach ($pattern in $ignoreFiles) {
            if ($_.Name -like $pattern) { return $false }
        }
        return $true
    } | Sort-Object FullName

    $treeLines = [System.Collections.Generic.List[string]]::new()
    $rootName = Split-Path $Root -Leaf
    $treeLines.Add("$rootName/")

    foreach ($item in $items) {
        $relPath = $item.FullName.Substring($Root.Length).TrimStart('\', '/').Replace('\', '/')
        $depth = ($relPath -split '/').Count
        $indent = "  " * $depth
        $name = $item.Name + $(if ($item.PSIsContainer) { "/" } else { "" })
        $treeLines.Add("$indent$name")
    }

    return ($treeLines -join "`n")
}

Write-Host "Gathering project tree..." -ForegroundColor Cyan
$compactTree = Get-CompactProjectTree -Root $repoRoot
Append-Block -Tag "project_structure" -Content $compactTree

# ----------------------------------------------------------------------
# 2. Prioritized Codebase & Configuration Files
# ----------------------------------------------------------------------
$orderedFiles = @(
    "README.md",
    "DEVELOPER_INSTRUCTION.md",
    "pyproject.toml",
    "src/causal_inference/config.py",
    "src/causal_inference/services/data_ingestion.py",
    "src/causal_inference/core/dml_engine.py",
    "src/causal_inference/services/artifact_manager.py",
    "src/causal_inference/main.py",
    "src/causal_inference/api/app.py",
    "tests/integration/test_dml_recovery.py",
    "tests/unit/test_data_ingestion.py",
    "tests/unit/test_artifact_manager.py",
    "Makefile",
    ".github/workflows/ci.yml"
)

foreach ($relPath in $orderedFiles) {
    $fullPath = Join-Path $repoRoot $relPath
    if (Test-Path $fullPath) {
        Write-Host "Adding file: $relPath" -ForegroundColor Gray
        $content = Get-Content -Path $fullPath -Raw -Encoding UTF8
        Append-Block -Tag "file" -Attributes "path=""$relPath""" -Content $content
    } else {
        Write-Warning "File missing: $relPath"
    }
}

# ----------------------------------------------------------------------
# 3. Supplemental Data & Artifact Signatures
# ----------------------------------------------------------------------
$csvSamplePath = Join-Path $repoRoot "data/raw/oj_data.csv"
if (Test-Path $csvSamplePath) {
    Write-Host "Extracting data sample from: data/raw/oj_data.csv" -ForegroundColor Gray
    $csvSample = (Get-Content -Path $csvSamplePath -TotalCount 6 -Encoding UTF8) -join "`n"
    Append-Block -Tag "data_sample" -Attributes "path=""data/raw/oj_data.csv (first 5 rows)""" -Content $csvSample
} else {
    $syntheticSample = @"
Purchase,WeekofPurchase,StoreID,PriceCH,PriceMM,DiscCH,DiscMM,SpecialCH,SpecialMM,LoyalCH,SalePriceMM,SalePriceCH,PriceDiff,Store7,PctDiscMM,PctDiscCH,ListPriceDiff,STORE
CH,237,1,1.75,1.99,0,0,0,0,0.5,1.99,1.75,0.24,No,0,0,0.24,1
MM,239,1,1.75,1.99,0,0,0,0,0.4,1.99,1.75,0.24,No,0,0,0.24,1
CH,245,1,1.86,2.09,0.17,0,0,0,0.6,2.09,1.69,0.4,No,0,0.091398,0.23,1
MM,227,1,1.69,1.69,0,0,0,0,0.25,1.69,1.69,0,No,0,0,0,1
CH,228,7,1.69,1.69,0,0,0,0,0.6,1.69,1.69,0,Yes,0,0,0,0
"@
    Append-Block -Tag "data_sample" -Attributes "path=""data/raw/oj_data.csv (schema reference)""" -Content $syntheticSample
}

$metricsPath = Join-Path $repoRoot "data/processed/model_metrics.json"
if (Test-Path $metricsPath) {
    Write-Host "Adding artifact: data/processed/model_metrics.json" -ForegroundColor Gray
    $metricsContent = Get-Content -Path $metricsPath -Raw -Encoding UTF8
    Append-Block -Tag "artifact" -Attributes "path=""data/processed/model_metrics.json""" -Content $metricsContent
} else {
    $syntheticMetrics = @"
{
    "marginal_effect": -0.4604,
    "p_value": 0.0001,
    "baseline_prob": 0.6103
}
"@
    Append-Block -Tag "artifact" -Attributes "path=""data/processed/model_metrics.json (schema reference)""" -Content $syntheticMetrics
}

# ----------------------------------------------------------------------
# 4. Save to File & Copy to Clipboard
# ----------------------------------------------------------------------
$finalText = $sb.ToString().TrimEnd()

$targetDir = Split-Path $OutputPath -Parent
if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

Set-Content -Path $OutputPath -Value $finalText -Encoding UTF8
Write-Host "Context generated at: $OutputPath" -ForegroundColor Green

try {
    Set-Clipboard -Value $finalText
    Write-Host "Context copied to clipboard ($($finalText.Length) characters)." -ForegroundColor Green
} catch {
    Write-Warning "Could not access clipboard directly. File written to $OutputPath."
}