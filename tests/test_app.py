__package__ = None

import json

import pytest

from .create_test_db import create_test_db
from devgrid_challenge.src.app import app

create_test_db()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    yield client


def test_get_with_existing_id(client):
    user_id = 11111
    req = client.get(f"/weather?id={user_id}")
    assert req.status_code == 200


def test_get_with_unexistent_id(client):
    user_id = 000000

    req = client.get(f"/weather?id={user_id}")

    response_body = json.loads(req.data)

    assert req.status_code == 400
    assert response_body["message"] == "User identifier not found"


def test_post_with_valid_id(client):
    """
    Testing the main function with a valid id
    It must pass without raising any exception
    """
    url = "/weather"
    mimetype = "Application/json"

    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype
    }

    body = {
        "id": "33010"
    }

    result = client.post(url, data=json.dumps(body), headers=headers)

    print(result.data)
