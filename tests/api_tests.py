import os
import uuid

import pytest
import requests


API_URL = os.getenv("API_URL", "http://localhost:8001").rstrip("/")


@pytest.mark.api
def test_create_and_delete_senzor():
	"""A senzor can be created and subsequently deleted through the API."""
	payload = {
		"cod": f"pytest-senzor-{uuid.uuid4().hex}",
		"locatie": "pytest",
	}

	create_response = requests.post(
		f"{API_URL}/api/senzori",
		json=payload,
		timeout=10,
	)
	assert create_response.status_code in (200, 201), create_response.text

	senzor = create_response.json()
	senzor_id = senzor.get("id")
	assert senzor_id is not None, "The create response must contain the senzor id"

	delete_response = requests.delete(
		f"{API_URL}/api/senzori/{senzor_id}",
		timeout=10,
	)
	assert delete_response.status_code in (200, 204), delete_response.text
