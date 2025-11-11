# PowerShell script to set up Python virtual environment and install dependencies

# Check for Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed or not in PATH. Please install Python 3.8 or newer."
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".\venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
$venvActivate = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "Activating virtual environment..."
    & $venvActivate
} else {
    Write-Host "Could not find venv activation script."
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..."
pip install --upgrade pip

# Install requirements
Write-Host "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

Write-Host "\nSetup complete! Add your Binance API keys to the .env file."
