import pytest
import requests
import time
import logging

ENDPOINT = "127.0.0.1:5000/api/senzori"
RASPUNS_HTTP = 200
CONTENT_TYPE = "application/json"
TIMP_RASPUNS = 0.05  # secunde

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_endpoint_senzori():
    start_time = time.time()
    response = requests.get(f"http://{ENDPOINT}")
    elapsed_time = time.time() - start_time

    assert response.status_code == RASPUNS_HTTP, f"Expected status code {RASPUNS_HTTP}, got {response.status_code}"
    assert response.headers['Content-Type'] == CONTENT_TYPE, f"Expected content type {CONTENT_TYPE}, got {response.headers['Content-Type']}"
    assert elapsed_time < TIMP_RASPUNS, f"Response time exceeded {TIMP_RASPUNS} seconds, took {elapsed_time:.2f} seconds"

def test_json_schema():
    response = requests.get(f"http://{ENDPOINT}")
    data = response.json()

    assert isinstance(data, list), f"Expected a list, got {type(data)}"
    for item in data:
        assert 'cod' in item and 'locatie' in item, f"Missing expected keys in item: {item}"
        assert isinstance(item['cod'], str), f"Expected 'cod' to be a string, got {type(item['cod'])}"
        assert isinstance(item['locatie'], str), f"Expected 'locatie' to be a string, got {type(item['locatie'])}"


def test_one_sensor_response():
    # Create a sensor first
    payload = {
    "cod": "temp_001",
    "id": 1,
    "locatie": "curte"
    }
    create_response = requests.get(f"http://127.0.0.1:5000/api/senzori/1", json=payload)
    assert create_response.status_code == 200, f"Expected status code 200, got {create_response.status_code}"

    # Now get the list of sensors
    response = requests.get(f"http://127.0.0.1:5000/api/senzori/1")
    data = response.json()

    logger.info("Received data: %s", data)
    # TODO verify the response contains exactly one sensor with the expected values
    assert len(data) == 3, f"Expected one sensor in the list, got {len(data)}"
    assert data['cod'] == 'temp_001', f"Expected cod 'temp_001', got {data['cod']}"
    assert data['locatie'] == 'curte', f"Expected locatie 'curte', got {data['locatie']}"


def test_inexistent_sensor():
    response = requests.get(f"http://127.0.0.1:5000/api/senzori/999")
    assert response.status_code == 404  , f"Expected status code 404, got {response.status_code}"


@pytest.fixture
def cleanup_test_sensor():
    def cleanup():
        response = requests.get(f"http://{ENDPOINT}")
        if response.ok:
            for sensor in response.json():
                if sensor.get("cod") == "temp_pytest_002" and "id" in sensor:
                    requests.delete(f"http://{ENDPOINT}/{sensor['id']}")

    cleanup()  # rulează înainte de test
    yield       # testul folosește fixture-ul aici
    cleanup()  # rulează după test

    # Doar înainte: păstrezi primul cleanup() și elimini al doilea.
    # Doar după: elimini primul cleanup() și păstrezi cleanup() de după yield.


def test_post_sensor(cleanup_test_sensor):
    
    payload = {
        "cod": "temp_pytest_002",
        "locatie": "garaj"
    }
    response = requests.post(f"http://127.0.0.1:5000/api/senzori", json=payload)
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"

def test_post_sensor_already_exists(cleanup_test_sensor):
    payload = {
        "cod": "temp_pytest_002",
        "locatie": "garaj"
    }
    create_response = requests.post(f"http://{ENDPOINT}", json=payload)
    assert create_response.status_code == 201, f"Expected status code 201, got {create_response.status_code}"
    response = requests.post(f"http://127.0.0.1:5000/api/senzori", json=payload)
    assert response.status_code == 409, f"Expected status code 409, got {response.status_code}"



def test_post_invalid_sensor():
    payload = {
        "cod": "",
        "locatie": ""
    }
    response = requests.post(f"http://127.0.0.1:5000/api/senzori", json=payload)
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"


def test_status_endpoint():
    response = requests.get(f"http://127.0.0.1:5000/api/status")
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"

def test_status_endpoint_with_temperature():
    response = requests.get(f"http://127.0.0.1:5000/api/status?temperatura=30")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"