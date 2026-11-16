#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 -m pip install -r backend/requirements.txt
cd frontend && npm install && npm run build
cd ..
echo ""
echo "Installation complete."
echo "GUI access: http://localhost:8000"
echo "Run: ./run.sh"
