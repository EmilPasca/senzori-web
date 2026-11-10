import pytest


def test_get_lista_initial_goala(client):
    response = client.get('/api/senzori')
    assert response.status_code == 200
    assert response.get_json() == []


def test_post_creare_senzor(client):
    response = client.post('/api/senzori', json={
        'cod': 'TEMP101', 'locatie': 'Laborator'
    })
    assert response.status_code == 201
    assert response.get_json()['cod'] == 'TEMP101'
    assert len(client.get('/api/senzori').get_json()) == 1


@pytest.mark.parametrize('payload', [{}, {'cod': '', 'locatie': 'Lab'}, {'cod': 'X'}])
def test_post_date_invalide(client, payload):
    response = client.post('/api/senzori', json=payload)
    assert response.status_code == 400


def test_id_inexistent(client):
    assert client.get('/api/senzori/999').status_code == 404


def test_api_temperatura_prag(client):
    response = client.get('/api/status?temperatura=30.1')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ALERTA'}
