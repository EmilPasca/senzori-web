#!/usr/bin/env bash
set -euo pipefail

# Configure these variables or export them before running the script.
DATABASE="${DATABASE:-${DB_PATH:-./atelier_senzori.db}}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
PYTHON="${PYTHON:-python3}"

mkdir -p "$BACKUP_DIR"
timestamp=$(date +%Y%m%d_%H%M%S)
backup_file="$BACKUP_DIR/$(basename "$DATABASE")_${timestamp}.db"

command -v "$PYTHON" >/dev/null 2>&1 || {
	echo "Error: $PYTHON is not installed or not in PATH." >&2
	exit 1
}

if [[ ! -f "$DATABASE" ]]; then
	echo "Error: SQLite database not found: $DATABASE" >&2
	exit 1
fi

"$PYTHON" - "$DATABASE" "$backup_file" <<'PY'
import sqlite3
import sys

source_path, backup_path = sys.argv[1:3]
with sqlite3.connect(source_path) as source, sqlite3.connect(backup_path) as backup:
    source.backup(backup)
PY

echo "Database backup created: $backup_file"
