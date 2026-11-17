#!/usr/bin/env bash
set -euo pipefail

# Configure these variables or export them before running the script.
DATABASE="${DATABASE:-${DB_PATH:-./atelier_senzori.db}}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
PYTHON="${PYTHON:-python3}"
PSEUDONYMIZATION_KEY="${PSEUDONYMIZATION_KEY:-}"

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

PSEUDONYMIZATION_KEY="$PSEUDONYMIZATION_KEY" "$PYTHON" - "$DATABASE" "$backup_file" <<'PY'
import hashlib
import hmac
import os
import sqlite3
import sys

source_path, backup_path = sys.argv[1:3]
with sqlite3.connect(source_path) as source, sqlite3.connect(backup_path) as backup:
    source.backup(backup)

key = os.environ.get("PSEUDONYMIZATION_KEY") or os.urandom(32).hex()


def pseudonym(prefix, value):
    digest = hmac.new(
        key.encode("utf-8"),
        f"{prefix}:{value}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:12]
    return f"{prefix}_{digest}"


with sqlite3.connect(backup_path) as backup:
    backup.execute("BEGIN")
    for user_id, username in backup.execute(
        "SELECT id, username FROM users"
    ).fetchall():
        backup.execute(
            "UPDATE users SET username = ? WHERE id = ?",
            (pseudonym("user", username), user_id),
        )
    for sensor_id, cod, locatie in backup.execute(
        "SELECT id, cod, locatie FROM senzori"
    ).fetchall():
        backup.execute(
            """
            UPDATE senzori
            SET cod = ?, locatie = ?
            WHERE id = ?
            """,
            (
                pseudonym("sensor", cod),
                pseudonym("location", locatie),
                sensor_id,
            ),
        )
    backup.commit()
PY

echo "Pseudonymized database backup created: $backup_file"
