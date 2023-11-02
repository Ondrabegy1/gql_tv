import pytest


from .client import createGQLClient

def test_client_read():
    client = createGQLClient()
    json = {
        'query': """query($id: UUID!){ eventById(id: $id) {id} }""",
        'variables': {
            'id': '45b2df80-ae0f-11ed-9bd8-0242ac110002'
        }
    }
    headers = {"Authorization": "Bearer 2d9dc5ca-a4a2-11ed-b9df-0242ac120003"}
    response = client.post("/gql", headers=headers, json=json)
    assert response.status_code == 200
    response = response.json()
    print(response)
    assert response.get("error", None) is None
    data = response.get("data", None)
    assert data is not None
    #assert False