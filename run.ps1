# Convenience launcher for Windows PowerShell
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs
)

$pythonExe = $null

# Check if python works
try {
    $ver = & python --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $pythonExe = "python"
    }
} catch {}

if (-not $pythonExe) {
    $candidatePaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:ProgramFiles\Python313\python.exe",
        "C:\Python313\python.exe"
    )
    foreach ($p in $candidatePaths) {
        if (Test-Path $p) {
            $pythonExe = $p
            break
        }
    }
}

if (-not $pythonExe) {
    Write-Error "Python executable not found. Please install Python 3.10+ or add it to PATH."
    exit 1
}

$mainScript = Join-Path $PSScriptRoot "main.py"
& $pythonExe $mainScript @ScriptArgs
