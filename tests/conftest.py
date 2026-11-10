import pytest
from app import create_app


@pytest.fixture
def client(tmp_path):
    # Baza este creata automat de create_app, intr-un director temporar.
    app = create_app(tmp_path / 'test.db')
    app.config.update(TESTING=True)
    return app.test_client()
