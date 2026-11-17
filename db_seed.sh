#!/usr/bin/env bash
set -euo pipefail

DB_PATH="${DB_PATH:-app.db}"
LOG_PATH="${LOG_PATH:-db_seed.log}"

log() {
	local message="$(date '+%Y-%m-%d %H:%M:%S') - $1"
	printf '%s\n' "$message" | tee -a "$LOG_PATH"
}

log "Starting database seed for $DB_PATH"

sqlite3 "$DB_PATH" <<'SQL'
CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT NOT NULL UNIQUE,
	password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS senzori (
	id INTEGER PRIMARY KEY,
	cod TEXT NOT NULL UNIQUE,
	locatie TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS citiri (
	id INTEGER PRIMARY KEY,
	senzor_id INTEGER NOT NULL,
	temperatura REAL NOT NULL,
	moment TEXT NOT NULL,
	FOREIGN KEY (senzor_id) REFERENCES senzori(id)
);

INSERT OR IGNORE INTO users (username, password) VALUES
	('user01', 'Password01!'),
	('user02', 'Password02!'),
	('user03', 'Password03!'),
	('user04', 'Password04!'),
	('user05', 'Password05!'),
	('user06', 'Password06!'),
	('user07', 'Password07!'),
	('user08', 'Password08!'),
	('user09', 'Password09!'),
	('user10', 'Password10!');
SQL

log "Database schema created or already exists"
log "Users seeded successfully"
log "Database seed completed"
