import pytest
import logging

from .client import createGQLClient

def test_client_read():
    client = createGQLClient()
    json = {
        'query': """query($id: UUID!){ result: eventById(id: $id) {id} }""",
        'variables': {
            'id': '45b2df80-ae0f-11ed-9bd8-0242ac110002'
        }
    }
    headers = {"Authorization": "Bearer 2d9dc5ca-a4a2-11ed-b9df-0242ac120003"}
    response = client.post("/gql", headers=headers, json=json)
    assert response.status_code == 200
    response = response.json()
    logging.info(response)
    assert response.get("error", None) is None
    data = response.get("data", None)
    assert data is not None
    #assert False


def test_client_hello_world():
    client = createGQLClient()
    json = {
        'query': """{ hello }""",
        'variables': {
            'id': '45b2df80-ae0f-11ed-9bd8-0242ac110002'
        }
    }
    headers = {"Authorization": "Bearer 2d9dc5ca-a4a2-11ed-b9df-0242ac120003"}
    response = client.post("/gql", headers=headers, json=json)
    assert response.status_code == 200
    response = response.json()
    logging.info(response)
    assert response.get("error", None) is None
    data = response.get("data", None)
    assert data is not None

def test_client_auth_ok():
    client = createGQLClient()
    json = {
        'query': """query($id: UUID!){ result: eventById(id: $id) { id sensitiveMsg }}""",
        'variables': {
            'id': '45b2df80-ae0f-11ed-9bd8-0242ac110002'
        }
    }
    headers = {"Authorization": "Bearer 2d9dc5ca-a4a2-11ed-b9df-0242ac120003"}
    response = client.post("/gql", headers=headers, json=json)
    assert response.status_code == 200
    response = response.json()
    logging.info(response)
    assert response.get("error", None) is None
    data = response.get("data", None)
    assert data is not None
    result = data.get("result", None)
    assert result is not None
    sensitiveMsg = result.get("sensitiveMsg", None)
    assert sensitiveMsg is not None
    assert sensitiveMsg == "sensitive information"
    #assert False

def test_client_auth_notok():
    client = createGQLClient()
    json = {
        'query': """query($id: UUID!){ result: eventById(id: $id) { id sensitiveMsg }}""",
        'variables': {
            'id': '45b2df80-ae0f-11ed-9bd8-0242ac110002'
        }
    }
    headers = {}
    logging.info("test_client_auth_notok.response")
    try:
        response = client.post("/gql", headers=headers, json=json)
    except:
        pass
    
    logging.info("test_client_auth_notok.response")
    assert response.status_code == 200
    response = response.json()
    logging.info(response)
    assert response.get("error", None) is None
    data = response.get("data", None)
    assert data is not None
    result = data.get("result", None)
    assert result is not None
    sensitiveMsg = result.get("sensitiveMsg", None)
    assert sensitiveMsg is None
    #assert False