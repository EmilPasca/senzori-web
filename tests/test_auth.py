import sqlite3
import uuid
from pathlib import Path

from werkzeug.security import check_password_hash

from app import app

DATABASE = Path(__file__).resolve().parents[1] / "atelier_senzori.db"


def test_login_page_is_available_without_authentication():
    client = app.test_client()

    response = client.get("/login")

    assert response.status_code == 200
    assert "Autentificare" in response.get_data(as_text=True)


def test_profile_requires_login():
    client = app.test_client()

    response = client.get("/profil")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_login_rejects_invalid_credentials():
    client = app.test_client()

    response = client.post(
        "/login",
        data={"username": "admin", "password": "wrong"},
    )

    assert response.status_code == 401
    assert "incorectă" in response.get_data(as_text=True)


def test_demo_user_is_stored_in_database():
    with sqlite3.connect(DATABASE) as con:
        user = con.execute(
            "SELECT username, password FROM users WHERE username = ?",
            ("admin",),
        ).fetchone()

        assert user[0] == "admin"
    assert user[1].startswith(("scrypt:", "pbkdf2:"))


def test_login_shows_authenticated_user_on_profile():
    client = app.test_client()

    response = client.post(
        "/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Ești autentificat ca" in response.get_data(as_text=True)
    assert "admin" in response.get_data(as_text=True)


def test_logout_clears_authenticated_session():
    client = app.test_client()
    client.post("/login", data={"username": "admin", "password": "admin123"})

    response = client.post("/logout", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    assert client.get("/profil").headers["Location"].endswith("/login")


def test_sensor_access_is_limited_to_owner():
    with sqlite3.connect(DATABASE) as con:
        alina_sensor_id = con.execute(
            "SELECT id FROM senzori WHERE cod = 'ALINA-TEMP-01'"
        ).fetchone()[0]

    client = app.test_client()
    client.post("/login", data={"username": "cosmin", "password": "cosmin123"})

    html_response = client.get(f"/senzori/{alina_sensor_id}")
    api_response = client.get(f"/api/senzori/{alina_sensor_id}")

    assert html_response.status_code == 403
    assert api_response.status_code == 403


def test_sensor_owner_can_access_sensor():
    with sqlite3.connect(DATABASE) as con:
        alina_sensor_id = con.execute(
            "SELECT id FROM senzori WHERE cod = 'ALINA-TEMP-01'"
        ).fetchone()[0]

    client = app.test_client()
    client.post("/login", data={"username": "alina", "password": "alina123"})

    assert client.get(f"/senzori/{alina_sensor_id}").status_code == 200
    assert client.get(f"/api/senzori/{alina_sensor_id}").status_code == 200


def test_password_is_not_stored_in_plain_text():
    with sqlite3.connect(DATABASE) as con:
        user = con.execute(
            "SELECT password FROM users WHERE username = 'admin'"
        ).fetchone()

    assert user is not None
    assert user[0] != "admin123"
    assert check_password_hash(user[0], "admin123")


def test_login_rejects_missing_fields():
    client = app.test_client()

    response = client.post("/login", data={"username": "", "password": ""})

    assert response.status_code == 400


def test_public_and_authenticated_html_routes():
    client = app.test_client()

    assert client.get("/").status_code == 200
    assert (
        client.get("/salut/Marian").get_data(as_text=True).startswith("Salut, Marian!")
    )
    assert client.get("/senzori").status_code == 302
    assert client.get("/form").status_code == 302

    client.post("/login", data={"username": "alina", "password": "alina123"})

    assert client.get("/profil").status_code == 200
    assert client.get("/senzori").status_code == 200
    assert client.get("/form").status_code == 200


def test_form_create_and_duplicate_sensor():
    client = app.test_client()
    client.post("/login", data={"username": "alina", "password": "alina123"})
    cod = f"FORM-{uuid.uuid4().hex}"

    created = client.post("/form", data={"cod": cod, "locatie": "Test location"})
    duplicate = client.post("/form", data={"cod": cod, "locatie": "Other location"})

    assert created.status_code == 302
    assert duplicate.status_code == 409


def test_form_rejects_missing_fields():
    client = app.test_client()
    client.post("/login", data={"username": "alina", "password": "alina123"})

    assert client.post("/form", data={"cod": "", "locatie": ""}).status_code == 400


def test_api_requires_authentication():
    client = app.test_client()

    assert client.get("/api/senzori").status_code == 401
    assert client.get("/api/senzori/1").status_code == 401


def test_api_crud_and_validation():
    client = app.test_client()
    client.post("/login", data={"username": "alina", "password": "alina123"})
    cod = f"API-{uuid.uuid4().hex}"

    assert client.post("/api/senzori", json=[]).status_code == 400
    assert (
        client.post("/api/senzori", json={"cod": "", "locatie": "Test"}).status_code
        == 400
    )
    assert (
        client.post("/api/senzori", json={"cod": cod, "locatie": ""}).status_code == 400
    )

    created = client.post("/api/senzori", json={"cod": cod, "locatie": "Test"})
    assert created.status_code == 201
    sensor_id = created.get_json()["id"]

    assert client.get("/api/senzori").status_code == 200
    assert client.get(f"/api/senzori/{sensor_id}").status_code == 200

    updated = client.put(
        f"/api/senzori/{sensor_id}",
        json={"cod": f"UPDATED-{uuid.uuid4().hex}", "locatie": "Updated"},
    )
    assert updated.status_code == 200

    assert (
        client.put(
            f"/api/senzori/{sensor_id}", json={"cod": "", "locatie": "Updated"}
        ).status_code
        == 400
    )
    assert (
        client.put(
            f"/api/senzori/{sensor_id}", json={"cod": "Updated", "locatie": ""}
        ).status_code
        == 400
    )
    assert client.put(f"/api/senzori/{sensor_id}", json=[]).status_code == 400

    assert client.delete(f"/api/senzori/{sensor_id}").status_code == 200
    assert client.delete(f"/api/senzori/{sensor_id}").status_code == 404


def test_api_returns_not_found_and_duplicate_conflict():
    client = app.test_client()
    client.post("/login", data={"username": "alina", "password": "alina123"})

    assert client.get("/api/senzori/999999").status_code == 404
    assert (
        client.put("/api/senzori/999999", json={"cod": "X", "locatie": "Y"}).status_code
        == 404
    )
    assert client.delete("/api/senzori/999999").status_code == 404

    duplicate = client.post(
        "/api/senzori",
        json={"cod": "ALINA-TEMP-01", "locatie": "Duplicate"},
    )
    assert duplicate.status_code == 409


def test_sensor_page_for_unknown_sensor():
    client = app.test_client()
    client.post("/login", data={"username": "alina", "password": "alina123"})

    assert client.get("/senzori/999999").status_code == 404
