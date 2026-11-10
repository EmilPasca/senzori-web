"""Mini-aplicatie Flask+SQLite pentru demonstratiile de testare.

Este o versiune autocontinuta a registrului de senzori din modulele anterioare.
Nu folositi serverul Flask de dezvoltare pentru evaluari reale de capacitate.
"""
from pathlib import Path
from contextlib import contextmanager
import sqlite3
from flask import Flask, jsonify, redirect, render_template, request, url_for
from logic import clasifica_temperatura


def create_app(db_path=None):
    app = Flask(__name__)
    default_db = Path(__file__).resolve().parent / 'atelier_senzori.db'
    app.config['DB_PATH'] = str(db_path or default_db)

    @contextmanager
    def connect():
        con = sqlite3.connect(app.config['DB_PATH'])
        con.row_factory = sqlite3.Row
        con.execute('PRAGMA foreign_keys = ON')
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    with connect() as con:
        con.execute('''CREATE TABLE IF NOT EXISTS senzori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cod TEXT NOT NULL UNIQUE,
            locatie TEXT NOT NULL
        )''')

    def get_all():
        with connect() as con:
            rows = con.execute('SELECT id, cod, locatie FROM senzori ORDER BY id').fetchall()
        return [dict(r) for r in rows]

    def validate(payload):
        if not isinstance(payload, dict):
            return None, 'Trimite un obiect JSON'
        cod = payload.get('cod', '')
        locatie = payload.get('locatie', '')
        if not isinstance(cod, str) or not isinstance(locatie, str):
            return None, 'Codul si locatia trebuie sa fie text'
        cod, locatie = cod.strip(), locatie.strip()
        if not cod or not locatie:
            return None, 'Codul si locatia sunt obligatorii'
        return {'cod': cod, 'locatie': locatie}, None

    @app.get('/')
    def home():
        return redirect(url_for('lista_web'))

    @app.get('/senzori')
    def lista_web():
        return render_template('senzori.html', senzori=get_all())

    @app.post('/senzori')
    def adauga_web():
        data, err = validate(request.form.to_dict())
        if err:
            return err, 400
        try:
            with connect() as con:
                con.execute('INSERT INTO senzori (cod, locatie) VALUES (?, ?)',
                            (data['cod'], data['locatie']))
        except sqlite3.IntegrityError:
            return 'Codul exista deja', 409
        return redirect(url_for('lista_web'))

    @app.get('/api/senzori')
    def lista_api():
        return jsonify(get_all())

    @app.get('/api/senzori/<int:senzor_id>')
    def detaliu_api(senzor_id):
        with connect() as con:
            row = con.execute('SELECT id, cod, locatie FROM senzori WHERE id=?',
                              (senzor_id,)).fetchone()
        if row is None:
            return jsonify(error='Senzor inexistent'), 404
        return jsonify(dict(row))

    @app.post('/api/senzori')
    def creeaza_api():
        data, err = validate(request.get_json(silent=True))
        if err:
            return jsonify(error=err), 400
        try:
            with connect() as con:
                cursor = con.execute(
                    'INSERT INTO senzori (cod, locatie) VALUES (?, ?)',
                    (data['cod'], data['locatie']))
                sensor_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            return jsonify(error='Codul exista deja'), 409
        return jsonify(id=sensor_id, **data), 201

    @app.patch('/api/senzori/<int:senzor_id>')
    def actualizeaza_api(senzor_id):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or 'locatie' not in payload:
            return jsonify(error='Camp locatie obligatoriu'), 400
        locatie = payload['locatie']
        if not isinstance(locatie, str) or not locatie.strip():
            return jsonify(error='Locatie invalida'), 400
        with connect() as con:
            cursor = con.execute('UPDATE senzori SET locatie=? WHERE id=?',
                                 (locatie.strip(), senzor_id))
        if cursor.rowcount == 0:
            return jsonify(error='Senzor inexistent'), 404
        return jsonify(id=senzor_id, locatie=locatie.strip())

    @app.delete('/api/senzori/<int:senzor_id>')
    def sterge_api(senzor_id):
        with connect() as con:
            cursor = con.execute('DELETE FROM senzori WHERE id=?', (senzor_id,))
        return ('', 204) if cursor.rowcount else (jsonify(error='Senzor inexistent'), 404)

    @app.get('/api/status')
    def status_api():
        temperatura = request.args.get('temperatura', type=float)
        try:
            status = clasifica_temperatura(temperatura)
        except ValueError:
            return jsonify(error='Temperatura invalida'), 400
        return jsonify(status=status)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=False)
