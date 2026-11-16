# Oracle SQL Execution Plan Analyzer & Visual Query Optimizer

## Setup
```bash
./install.sh
./run.sh
```
Open http://localhost:8000

## Features
- Paste SQL + DBMS_XPLAN output or use sample.
- Stacked Current vs AI-Optimized plan graphs.
- React Flow + Dagre LR layout.

## Limitations
- Backend returns static sample graphs; full hierarchical plan parsing not implemented.
- LLM optimization is rule-based suggestions, not live AI.
- No live Oracle DB connection in this prototype.

## Working Principle
1. Frontend sends SQL + plan text to FastAPI `/api/analyze`.
2. Backend parses plan rows and builds node/edge graphs.
3. React Flow renders Current and AI-Optimized panels side-by-side.
4. Suggestions and optimized SQL are displayed.

## Requirements
- Python 3.10+
- Node.js 18+
- npm

## Install Procedure
```bash
./install.sh   # installs Python deps, npm deps, builds frontend
./run.sh       # starts server on port 8000
```
Uninstall:
```bash
./uninstall.sh
```
