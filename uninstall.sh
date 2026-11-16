#!/usr/bin/env bash
cd "$(dirname "$0")"
# stop any process on port 8000
if command -v fuser >/dev/null 2>&1; then fuser -k 8000/tcp 2>/dev/null || true; fi
pkill -f "python3 main.py" 2>/dev/null || true
rm -rf frontend/dist frontend/node_modules backend/__pycache__
echo "Uninstalled. Run ./install.sh to reinstall."
