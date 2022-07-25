import os
import json

import pytest

from .test_db_manager import create_test_db, delete_tested_rows
from devgrid_challenge.src.app import app

create_test_db()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    yield client


def test_env_exists():
    assert os.path.exists("../src/.env")


def test_post_with_valid_id(client):
    """
    Testing the main function with a valid id
    It must pass without raising any exception
    """
    user_id = "330104"

    url = "/weather"
    mimetype = "Application/json"

    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype
    }

    body = {
        "user_id": user_id
    }

    result = client.post(url, data=json.dumps(body), headers=headers)

    response_body = json.loads(result.data)

    assert result.status_code == 200
    assert response_body == {"message": "All cities collected."}

    delete_tested_rows(user_id)


def test_post_with_existent_id(client):
    user_id = "123456"

    url = "/weather"
    mimetype = "Application/json"

    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype
    }

    body = {
        "user_id": user_id
    }

    result = client.post(url, data=json.dumps(body), headers=headers)

    response_body = json.loads(result.data)

    assert result.status_code == 400
    assert response_body == {"message": "Invalid 'user_id'. It must contain "
                                        "only numbers and be unique."}


def test_post_with_wrong_value_id(client):
    user_id = "1q2w3e"

    url = "/weather"
    mimetype = "Application/json"

    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype
    }

    body = {
        "user_id": user_id
    }

    result = client.post(url, data=json.dumps(body), headers=headers)

    response_body = json.loads(result.data)

    assert result.status_code == 400
    assert response_body == {"message": "Invalid 'user_id'. It must contain "
                                        "only numbers and be unique."}


def test_post_with_wrong_type_id(client):
    """
        Testing the main insertion function with an INVALID id
        It must throw an exception
        """
    user_id = {
        "id_type": "dict"
    }

    url = "/weather"
    mimetype = "Application/json"

    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype
    }

    body = {
        "user_id": user_id
    }

    result = client.post(url, data=json.dumps(body), headers=headers)

    response_body = json.loads(result.data)

    assert result.status_code == 400
    assert response_body == {"message": "Invalid 'user_id'. It must contain "
                                        "only numbers and be unique."}


def test_post_with_wrong_body(client):
    user_id = {
        "id_type": "dict"
    }

    url = "/weather"
    mimetype = "Application/json"

    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype
    }

    body = {
        "test": user_id
    }

    result = client.post(url, data=json.dumps(body), headers=headers)

    response_body = json.loads(result.data)

    assert result.status_code == 400
    assert response_body == {"message": "Missing param 'user_id'."}


def test_get_with_existent_id(client):
    user_id = 123456
    result = client.get(f"/weather?user-id={user_id}")
    assert result.status_code == 200


def test_get_with_unexistent_id(client):
    user_id = "000000"

    result = client.get(f"/weather?user-id={user_id}")

    response_body = json.loads(result.data)

    assert result.status_code == 400
    assert response_body == {"message": "User identifier not found."}


def test_get_without_id(client):
    result = client.get("/weather")

    response_body = json.loads(result.data)

    assert result.status_code == 400
    assert response_body == {"message": "Missing query param 'user-id'."}


def test_get_with_wrong_format_id(client):
    user_id = "1q2w3e"

    result = client.get(f"/weather?user-id={user_id}")

    response_body = json.loads(result.data)

    assert result.status_code == 400
    assert response_body == {"message": "Invalid 'user-id'. It must contain "
                                        "only numbers and be unique."}
