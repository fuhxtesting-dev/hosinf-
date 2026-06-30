#!/bin/bash
# FX HOSTING - Start Script for Termux & Linux
# Usage: bash start.sh

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║   ███████╗██╗  ██╗    ██╗  ██╗ ██████╗ ███████╗████████╗ ║"
echo "║   ██╔════╝╚██╗██╔╝    ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝ ║"
echo "║   █████╗   ╚███╔╝     ███████║██║   ██║███████╗   ██║    ║"
echo "║   ██╔══╝   ██╔██╗     ██╔══██║██║   ██║╚════██║   ██║    ║"
echo "║   ██║     ██╔╝ ██╗    ██║  ██║╚██████╔╝███████║   ██║    ║"
echo "║   ╚═╝     ╚═╝  ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝    ║"
echo "║                                                          ║"
echo "║   Ultimate VPS Management Panel v3.0.0                   ║"
echo "║   Optimized for Termux & Linux VPS                       ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "[ERROR] Python is not installed!"
    echo "Install with: pkg install python (Termux) or apt install python3"
    exit 1
fi

echo "[FX HOSTING] Using Python: $($PYTHON --version)"
echo "[FX HOSTING] Checking dependencies..."

# Install dependencies if needed
if [ ! -d "__pycache__" ]; then
    echo "[FX HOSTING] Installing dependencies..."
    $PYTHON -m pip install -r requirements.txt --quiet
fi

echo "[FX HOSTING] Starting server..."
echo "[FX HOSTING] Access the panel at: http://localhost:5000"
echo "[FX HOSTING] Default passwords:"
echo "  Admin: FXHOSTING2024"
echo "  User:  admin"
echo ""

# Start the application
$PYTHON app.py
