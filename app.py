import sqlite3
import os
import time
import logging

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-secret-key")

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

# Demo credentials for this educational application. Use a proper user store in production.
USERS = {"admin": "admin123"}

@app.get("/")
def acasa():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            return render_template(
                "login.html",
                error="Completează numele de utilizator și parola.",
                username=username,
            ), 400

        if USERS.get(username) != password:
            return render_template(
                "login.html",
                error="Nume de utilizator sau parolă incorectă.",
                username=username,
            ), 401

        session["username"] = username
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
    return f"Senzorul cu ID-ul {senzor_id}."

@app.get("/senzori")
def lista_senzori():
    print("Se generează lista cu senzori...") 
    return render_template("senzori.html",
                           senzori=citeste_senzori_din_baza_de_date())

@app.get("/form")
def afiseaza_formular():
    return render_template("form.html")

@app.post("/form")
def adauga_senzor():
    cod = request.form.get("cod", "").strip()
    locatie = request.form.get("locatie", "").strip()
    if not cod or not locatie:
        return "Câmpuri obligatorii", 400
    with sqlite3.connect("atelier_senzori.db") as con:
        con.execute("INSERT INTO senzori(cod, locatie) VALUES (?, ?)",
                    (cod, locatie))
        con.commit()
        print(f"Senzorul cu cod '{cod}' și locație '{locatie}' a fost adăugat în baza de date.")

    return redirect(url_for("lista_senzori"))




def citeste_senzori_din_baza_de_date():
    with sqlite3.connect("atelier_senzori.db") as con:
        con.row_factory = sqlite3.Row
        randuri = con.execute(
            "SELECT id, cod, locatie FROM senzori ORDER BY id"
        ).fetchall()
        print(f"Am citit {len(randuri)} senzori din baza de date.")
    return [dict(r) for r in randuri]


# Path-uri pentru API RESTful

@app.get("/api/senzori")
def api_lista_senzori():
    return jsonify(citeste_senzori_din_baza_de_date())

@app.get("/api/senzori/<int:senzor_id>")
def api_senzor(senzor_id):
    with sqlite3.connect("atelier_senzori.db") as con:
        con.row_factory = sqlite3.Row
        row = con.execute(
            "SELECT id, cod, locatie FROM senzori WHERE id = ?",
            (senzor_id,)
        ).fetchone()
    if row is None:
        return jsonify({"error": "Senzor inexistent"}), 404
    return jsonify(dict(row))

@app.put("/api/senzori/<int:senzor_id>")
def api_senzor_update(senzor_id):
    with sqlite3.connect("atelier_senzori.db") as con:
        con.row_factory = sqlite3.Row
        row = con.execute(
            "SELECT id, cod, locatie FROM senzori WHERE id = ?",
            (senzor_id,)
        ).fetchone()
    if row is None:
        return jsonify({"error": "Senzor inexistent"}), 404
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
    with sqlite3.connect("atelier_senzori.db") as con:
        con.execute(
            "UPDATE senzori SET cod = ?, locatie = ? WHERE id = ?",
            (cod, locatie, senzor_id),
        )
        con.commit()

    return jsonify({"id": senzor_id, "cod": cod, "locatie": locatie})

@app.post("/api/senzori")
def api_creare():
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
    with sqlite3.connect("atelier_senzori.db") as con:
        cursor = con.execute(
            "INSERT INTO senzori(cod, locatie) VALUES (?, ?)",
            (cod, locatie),
        )
        senzor_id = cursor.lastrowid
        con.commit()

    return jsonify({
        "id": senzor_id,
        "cod": cod,
        "locatie": locatie,
    }), 201

@app.delete("/api/senzori/<int:senzor_id>")
def api_stergere(senzor_id):
    with sqlite3.connect("atelier_senzori.db") as con:
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