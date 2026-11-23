import sqlite3
import os
import time
import logging
import hmac

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-secret-key")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
DATABASE = os.environ.get(
    "DATABASE",
    os.path.join(os.path.dirname(__file__), "atelier_senzori.db"),
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.before_request
def log_request_start():
    request.start_time = time.perf_counter()


@app.after_request
def log_request_end(response):
    duration_ms = (time.perf_counter() - request.start_time) * 1000
    logger.info(
        "%s %s %s %s %.2fms",
        request.remote_addr or "-",
        request.method,
        request.full_path.rstrip("?"),
        response.status,
        duration_ms,
    )
    return response


@app.teardown_request
def log_request_error(error):
    if error is not None:
        duration_ms = (time.perf_counter() - getattr(request, "start_time", time.perf_counter())) * 1000
        logger.exception(
            "%s %s %s failed after %.2fms",
            request.remote_addr or "-",
            request.method,
            request.full_path.rstrip("?"),
            duration_ms,
        )

def initialize_database():
    logger.info("Initializing database: %s", DATABASE)
    with sqlite3.connect(DATABASE) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS senzori (
                id INTEGER PRIMARY KEY,
                cod TEXT NOT NULL UNIQUE,
                locatie TEXT NOT NULL,
                owner_user_id INTEGER,
                FOREIGN KEY (owner_user_id) REFERENCES users(id)
            )
            """
        )
        columns = {
            row[1] for row in con.execute("PRAGMA table_info(senzori)").fetchall()
        }
        if "owner_user_id" not in columns:
            con.execute("ALTER TABLE senzori ADD COLUMN owner_user_id INTEGER")
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS citiri (
                id INTEGER PRIMARY KEY,
                senzor_id INTEGER NOT NULL,
                temperatura REAL NOT NULL,
                moment TEXT NOT NULL,
                FOREIGN KEY (senzor_id) REFERENCES senzori(id)
            )
            """
        )
        con.execute(
            "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
            ("admin", generate_password_hash("admin123")),
        )
        con.executemany(
            "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
            [
                ("alina", generate_password_hash("alina123")),
                ("cosmin", generate_password_hash("cosmin123")),
            ],
        )
        legacy_users = con.execute(
            "SELECT id, username, password FROM users WHERE username IN (?, ?, ?)",
            ("admin", "alina", "cosmin"),
        ).fetchall()
        legacy_passwords = {
            "admin": "admin123",
            "alina": "alina123",
            "cosmin": "cosmin123",
        }
        for user_id, username, stored_password in legacy_users:
            if not stored_password.startswith(("scrypt:", "pbkdf2:")):
                con.execute(
                    "UPDATE users SET password = ? WHERE id = ?",
                    (generate_password_hash(legacy_passwords[username]), user_id),
                )

        users = dict(con.execute(
            "SELECT username, id FROM users WHERE username IN (?, ?)",
            ("alina", "cosmin"),
        ).fetchall())
        demo_sensors = [
            ("ALINA-TEMP-01", "Apartament Alina", users["alina"]),
            ("ALINA-UMID-01", "Balcon Alina", users["alina"]),
            ("COSMIN-TEMP-01", "Apartament Cosmin", users["cosmin"]),
        ]
        con.executemany(
            """
            INSERT OR IGNORE INTO senzori (cod, locatie, owner_user_id)
            VALUES (?, ?, ?)
            """,
            demo_sensors,
        )
        con.execute(
            """
            UPDATE senzori
            SET owner_user_id = (
                SELECT u.id FROM users u
                WHERE u.username = CASE
                    WHEN senzori.cod LIKE 'ALINA-%' THEN 'alina'
                    WHEN senzori.cod LIKE 'COSMIN-%' THEN 'cosmin'
                END
            )
            WHERE cod LIKE 'ALINA-%' OR cod LIKE 'COSMIN-%'
            """
        )
        con.commit()
    logger.info("Database initialized")


initialize_database()

@app.get("/")
def acasa():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        logger.info("Login attempt for user %r", username or "-")

        if not username or not password:
            logger.warning("Login rejected: missing username or password")
            return render_template(
                "login.html",
                error="Completează numele de utilizator și parola.",
                username=username,
            ), 400

        with sqlite3.connect(DATABASE) as con:
            user = con.execute(
                "SELECT id, username, password FROM users WHERE username = ?",
                (username,),
            ).fetchone()

        password_matches = False
        if user is not None:
            stored_password = user[2]
            if stored_password.startswith(("scrypt:", "pbkdf2:")):
                password_matches = check_password_hash(stored_password, password)
            else:
                password_matches = hmac.compare_digest(stored_password, password)
                if password_matches:
                    with sqlite3.connect(DATABASE) as con:
                        con.execute(
                            "UPDATE users SET password = ? WHERE id = ?",
                            (generate_password_hash(password), user[0]),
                        )
                        con.commit()

        if not password_matches:
            logger.warning("Login failed for user %r", username)
            return render_template(
                "login.html",
                error="Nume de utilizator sau parolă incorectă.",
                username=username,
            ), 401

        session["username"] = username
        logger.info("Login successful for user %r", username)
        return redirect(url_for("profil"))

    if "username" in session:
        return redirect(url_for("profil"))
    return render_template("login.html")


@app.get("/profil")
def profil():
    username = session.get("username")
    if username is None:
        return redirect(url_for("login"))
    return render_template("profile.html", username=username)


@app.post("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.get("/salut/<nume>")
def salut(nume):
    return f"Salut, {nume}! Bine ai venit în aplicația Flask."


@app.get("/senzori/<int:senzor_id>")
def senzori(senzor_id):
    if "username" not in session:
        return redirect(url_for("login"))
    sensor = citeste_senzor(senzor_id)
    if sensor is None:
        return "Senzor inexistent", 404
    if sensor["owner_username"] != session["username"]:
        return "Nu ai acces la acest senzor", 403
    return render_template("senzor.html", senzor=sensor)

@app.get("/senzori")
def lista_senzori():
    username = session.get("username")
    if username is None:
        return redirect(url_for("login"))
    print("Se generează lista cu senzori...")
    return render_template("senzori.html",
                           senzori=citeste_senzori_din_baza_de_date(username))

@app.get("/form")
def afiseaza_formular():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("form.html")

@app.post("/form")
def adauga_senzor():
    username = session.get("username")
    if username is None:
        return redirect(url_for("login"))
    cod = request.form.get("cod", "").strip()
    locatie = request.form.get("locatie", "").strip()
    if not cod or not locatie:
        return "Câmpuri obligatorii", 400
    with sqlite3.connect(DATABASE) as con:
        owner_id = con.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()[0]
        try:
            con.execute(
                """
                INSERT INTO senzori(cod, locatie, owner_user_id)
                VALUES (?, ?, ?)
                """,
                (cod, locatie, owner_id),
            )
            con.commit()
        except sqlite3.IntegrityError:
            return "Codul senzorului există deja", 409
        print(f"Senzorul cu cod '{cod}' și locație '{locatie}' a fost adăugat în baza de date.")

    return redirect(url_for("lista_senzori"))




def citeste_senzori_din_baza_de_date(username=None):
    with sqlite3.connect(DATABASE) as con:
        con.row_factory = sqlite3.Row
        if username is None:
            query = "SELECT id, cod, locatie, owner_user_id FROM senzori ORDER BY id"
            randuri = con.execute(query).fetchall()
        else:
            query = """
                SELECT s.id, s.cod, s.locatie, s.owner_user_id
                FROM senzori s
                JOIN users u ON u.id = s.owner_user_id
                WHERE u.username = ?
                ORDER BY s.id
            """
            randuri = con.execute(query, (username,)).fetchall()
        print(f"Am citit {len(randuri)} senzori din baza de date.")
    return [dict(r) for r in randuri]


def citeste_senzor(senzor_id):
    with sqlite3.connect(DATABASE) as con:
        con.row_factory = sqlite3.Row
        row = con.execute(
            """
            SELECT s.id, s.cod, s.locatie, u.username AS owner_username
            FROM senzori s
            LEFT JOIN users u ON u.id = s.owner_user_id
            WHERE s.id = ?
            """,
            (senzor_id,),
        ).fetchone()
    return dict(row) if row is not None else None


def senzorul_apartine_utilizatorului(senzor_id, username):
    with sqlite3.connect(DATABASE) as con:
        row = con.execute(
            """
            SELECT 1
            FROM senzori s
            JOIN users u ON u.id = s.owner_user_id
            WHERE s.id = ? AND u.username = ?
            """,
            (senzor_id, username),
        ).fetchone()
    return row is not None


# Path-uri pentru API RESTful

@app.get("/api/senzori")
def api_lista_senzori():
    username = session.get("username")
    if username is None:
        return jsonify({"error": "Autentificare necesară"}), 401
    return jsonify(citeste_senzori_din_baza_de_date(username))

@app.get("/api/senzori/<int:senzor_id>")
def api_senzor(senzor_id):
    username = session.get("username")
    if username is None:
        return jsonify({"error": "Autentificare necesară"}), 401
    sensor = citeste_senzor(senzor_id)
    if sensor is None:
        return jsonify({"error": "Senzor inexistent"}), 404
    if not senzorul_apartine_utilizatorului(senzor_id, username):
        return jsonify({"error": "Nu ai acces la acest senzor"}), 403
    return jsonify(sensor)

@app.put("/api/senzori/<int:senzor_id>")
def api_senzor_update(senzor_id):
    username = session.get("username")
    if username is None:
        return jsonify({"error": "Autentificare necesară"}), 401
    with sqlite3.connect(DATABASE) as con:
        con.row_factory = sqlite3.Row
        row = con.execute(
            "SELECT id, cod, locatie FROM senzori WHERE id = ?",
            (senzor_id,)
        ).fetchone()
    if row is None:
        return jsonify({"error": "Senzor inexistent"}), 404
    if not senzorul_apartine_utilizatorului(senzor_id, username):
        return jsonify({"error": "Nu ai acces la acest senzor"}), 403
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON invalid"}), 400
    cod = data.get("cod")
    locatie = data.get("locatie")
    if not isinstance(cod, str) or not cod.strip():
        return jsonify({"error": "Cod obligatoriu"}), 400
    if not isinstance(locatie, str) or not locatie.strip():
        return jsonify({"error": "Locație obligatorie"}), 400

    cod = cod.strip()
    locatie = locatie.strip()
    with sqlite3.connect(DATABASE) as con:
        try:
            con.execute(
                "UPDATE senzori SET cod = ?, locatie = ? WHERE id = ?",
                (cod, locatie, senzor_id),
            )
            con.commit()
        except sqlite3.IntegrityError:
            return jsonify({"error": "Codul senzorului există deja"}), 409

    return jsonify({"id": senzor_id, "cod": cod, "locatie": locatie})

@app.post("/api/senzori")
def api_creare():
    username = session.get("username")
    if username is None:
        return jsonify({"error": "Autentificare necesară"}), 401
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON invalid"}), 400
    cod = data.get("cod")
    locatie = data.get("locatie")
    if not isinstance(cod, str) or not cod.strip():
        return jsonify({"error": "Cod obligatoriu"}), 400
    if not isinstance(locatie, str) or not locatie.strip():
        return jsonify({"error": "Locație obligatorie"}), 400

    cod = cod.strip()
    locatie = locatie.strip()
    with sqlite3.connect(DATABASE) as con:
        owner_id = con.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()[0]
        try:
            cursor = con.execute(
                """
                INSERT INTO senzori(cod, locatie, owner_user_id)
                VALUES (?, ?, ?)
                """,
                (cod, locatie, owner_id),
            )
        except sqlite3.IntegrityError:
            return jsonify({"error": "Codul senzorului există deja"}), 409
        senzor_id = cursor.lastrowid
        con.commit()

    return jsonify({
        "id": senzor_id,
        "cod": cod,
        "locatie": locatie,
    }), 201

@app.delete("/api/senzori/<int:senzor_id>")
def api_stergere(senzor_id):
    username = session.get("username")
    if username is None:
        return jsonify({"error": "Autentificare necesară"}), 401
    with sqlite3.connect(DATABASE) as con:
        exists = con.execute(
            "SELECT 1 FROM senzori WHERE id = ?", (senzor_id,)
        ).fetchone()
    if exists is None:
        return jsonify({"error": "Senzor inexistent"}), 404
    if not senzorul_apartine_utilizatorului(senzor_id, username):
        return jsonify({"error": "Nu ai acces la acest senzor"}), 403
    with sqlite3.connect(DATABASE) as con:
        cursor = con.execute(
            "DELETE FROM senzori WHERE id = ?",
            (senzor_id,),
        )
        con.commit()
    if cursor.rowcount == 0:
        return jsonify({"error": "Senzor inexistent"}), 404
    return jsonify({"message": f"Senzorul cu ID-ul {senzor_id} a fost șters."}), 200



# În terminal:
# flask --app app run --debug