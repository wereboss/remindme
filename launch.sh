#!/usr/bin/env bash
# ==============================================================================
# Cross-Platform Launcher for Linux & macOS
# Notes & Reminders PWA (RemindMe)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo " Starting Notes & Reminders PWA Service "
echo " Platform: $(uname -s)"
echo "=========================================="

# Check for python3
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is not installed or not in PATH."
    echo "Please install Python 3.10+ from https://www.python.org/ or your package manager."
    exit 1
fi

# Create virtual environment if not present
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in .venv..."
    python3 -m venv .venv
fi

# Activate virtualenv
source .venv/bin/activate

# Install / update dependencies
echo "Verifying dependencies..."
pip install --quiet -r requirements.txt

# Bind port 9031
export PORT="${PORT:-9031}"

echo ""
echo "RemindMe PWA is running on:"
echo " -> Local:   http://localhost:${PORT}"
echo " -> Network: http://0.0.0.0:${PORT}"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

# Attempt to open browser on desktop (non-blocking)
if [ "$(uname -s)" = "Darwin" ]; then
    (sleep 1 && open "http://localhost:${PORT}") &>/dev/null &
elif command -v xdg-open &>/dev/null; then
    (sleep 1 && xdg-open "http://localhost:${PORT}") &>/dev/null &
fi

python3 run.py
