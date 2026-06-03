param(
    [string]$EnvFile = ".env.local"
)

Write-Host "Setting up development environment (PowerShell)"

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtualenv .venv"
    python -m venv .venv
}

$venvPython = Join-Path -Path ".venv" -ChildPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Cannot find venv python at $venvPython" -ForegroundColor Red
    exit 1
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

# Set sane defaults for local development if not already present
if (-not $env:DATABASE_URL) { $env:DATABASE_URL = "sqlite:///./dev.db" }
if (-not $env:ANTHROPIC_API_KEY) { $env:ANTHROPIC_API_KEY = "placeholder" }
if (-not $env:REAL_ESTATE_API_KEY) { $env:REAL_ESTATE_API_KEY = "placeholder" }
if (-not $env:LANGSMITH_TRACING) { $env:LANGSMITH_TRACING = "false" }

Write-Host "Initializing database tables..."
& $venvPython -m app.db.init_db

Write-Host "Starting development server (uvicorn) on http://0.0.0.0:8000"
& $venvPython -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
