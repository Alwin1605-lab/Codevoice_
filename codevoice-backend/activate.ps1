param(
    [switch]$Install,
    [switch]$Start,
    [string]$ServerHost = "0.0.0.0",
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

# Move to the backend folder (this script's directory)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Detect or create a virtual environment
$venvDir = Join-Path $scriptDir "venv"
if (-not (Test-Path "$venvDir\Scripts\Activate.ps1")) {
    $venvDir = Join-Path $scriptDir ".venv"
}

if (-not (Test-Path "$venvDir\Scripts\Activate.ps1")) {
    Write-Host "Creating virtual environment at $venvDir ..." -ForegroundColor Yellow
    python -m venv $venvDir
}

if (-not (Test-Path "$venvDir\Scripts\Activate.ps1")) {
    Write-Error "Could not find or create a virtual environment at $venvDir. Make sure Python is installed and on PATH."
    exit 1
}

# Activate the venv (provides 'deactivate' function and updates PATH)
& "$venvDir\Scripts\Activate.ps1"

# Load .env into current process environment (optional)
$envPath = Join-Path $scriptDir ".env"
if (Test-Path $envPath) {
    Get-Content $envPath | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith('#')) {
            $idx = $line.IndexOf('=')
            if ($idx -gt 0) {
                $key = $line.Substring(0, $idx).Trim()
                $val = $line.Substring($idx + 1).Trim().Trim('"').Trim("'")
                [System.Environment]::SetEnvironmentVariable($key, $val, 'Process')
            }
        }
    }
    Write-Host ".env loaded into current session." -ForegroundColor DarkGreen
}

if ($Install) {
    Write-Host "Installing dependencies from requirements.txt ..." -ForegroundColor Yellow
    pip install -r (Join-Path $scriptDir 'requirements.txt')
}

if ($Start) {
    Write-Host "Starting backend server (Uvicorn) ..." -ForegroundColor Yellow
    uvicorn main:app --reload --host $ServerHost --port $Port
} else {
    Write-Host "Virtual environment activated. Use 'deactivate' to exit." -ForegroundColor Green
    Write-Host "Optional flags: -Install to install deps, -Start to run the server." -ForegroundColor DarkGray
}