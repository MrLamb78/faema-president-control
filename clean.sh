#!/bin/sh
# Remove arquivos temporários gerados pelo SKiDL e Python
# Seguro para rodar a qualquer hora — tudo pode ser regenerado.

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "Limpando arquivos temporários em $ROOT ..."

# SKiDL: ERC reports, logs e libs auto-geradas
find "$ROOT" -maxdepth 2 -name "*.erc"      -not -path "*/.git/*" -delete
find "$ROOT" -maxdepth 2 -name "*.log"      -not -path "*/.git/*" -delete
find "$ROOT" -maxdepth 1 -name "*_sklib.py"                        -delete
find "$ROOT" -maxdepth 1 -name "skidl_REPL.*"                      -delete

# Python bytecode
find "$ROOT" -type d -name "__pycache__"    -not -path "*/.git/*" -not -path "*/.venv/*" -exec rm -rf {} + 2>/dev/null || true
find "$ROOT" -name "*.pyc"                  -not -path "*/.git/*" -not -path "*/.venv/*" -delete

# macOS metadata
find "$ROOT" -name ".DS_Store"              -not -path "*/.git/*" -delete

echo "Pronto."
