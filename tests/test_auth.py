from app import app
import sqlite3
from pathlib import Path


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

    assert user == ("admin", "admin123")


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
