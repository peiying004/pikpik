#!/bin/bash
set -e

echo "=== iOS GPS Simulator Setup ==="
echo ""
echo "Project files:"
echo "  app.py             - Flask server (main application)"
echo "  requirements.txt   - Python dependencies"
echo "  templates/index.html - Web UI"
echo "  start.command       - One-click launcher (tunneld + server)"
echo "  setup.sh            - This setup script"
echo ""

# Check macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "Error: This script only supports macOS."
    exit 1
fi

# Check/install Homebrew
if ! command -v brew &> /dev/null; then
    echo "[1/5] Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "[1/5] Homebrew already installed. Skipping."
fi

# Install Python 3.13 and libusb (iOS 18.2+ requires Python 3.13+)
echo "[2/5] Installing Python 3.13 and libusb via Homebrew..."
brew install python@3.13 libusb 2>/dev/null || true

# Create venv with Python 3.13
echo "[3/5] Creating Python virtual environment..."
if [[ -d "venv" ]]; then
    echo "  Removing old venv and rebuilding with Python 3.13..."
    rm -rf venv
fi
$(brew --prefix python@3.13)/bin/python3.13 -m venv venv

# Install pip packages
echo "[4/5] Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Make start.command executable
echo "[5/5] Setting permissions..."
chmod +x start.command

echo ""
echo "=== Setup complete ==="
echo ""
echo "To run (option 1 - double-click):"
echo "  Double-click start.command in Finder"
echo ""
echo "To run (option 2 - manual):"
echo "  sudo pymobiledevice3 remote tunneld &"
echo "  sleep 10"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Then open http://localhost:8080 in your browser."
