## Step 10

This step introduces a capability to use authorization tokens.

### Authentization & Authorization

Authentization is mechanism which ensures that questioner is That Entity (person).

Authorization is mechanism which ensures that questioner has proper right for particular operation (CRUD).

Quite often for authorization is used (http/s request) header item named Authorization.
This header item can have form `Authorization: Bearer ABCDEF`, where `ABCDEF` is token.

When asgi application receives an incomming request, it encodes information about request in data structure. In this case (strawberry) this structure is available at `context["request"]`.

According a token value it is possible to find a user which is owner of the valid token. This process has been encoded into `utils.Dataloaders.py`. There is function

```python
def getUser(info):
    context = info.context
    print(list(context.keys()))
    result = context.get("user", None)
    if result is None:
        authorization = context["request"].headers.get("Authorization", None)
        if authorization is not None:
            if 'Bearer ' in authorization:
                token = authorization.split(' ')[1]
                if token == "2d9dc5ca-a4a2-11ed-b9df-0242ac120003":
                    result = {
                        "id": "2d9dc5ca-a4a2-11ed-b9df-0242ac120003",
                        "name": "John",
                        "surname": "Newbie",
                        "email": "john.newbie@world.com"
                    }
                    context["user"] = result
    print("getUser", result)
    return result
```


If the function is called for the first time (during service of request), the user is recognized from token (if possible) and stored in `context["user"]`. Each consequent call take the user description from `context["user"]` directly.


### Testing

The function creating context for tests (see `testing.shared.py`) is extended into form:

```python
async def createContext(asyncSessionMaker):
    loadersContext = createLoadersContext(asyncSessionMaker)
    user = {
        "id": "2d9dc5ca-a4a2-11ed-b9df-0242ac120003",
        "name": "John",
        "surname": "Newbie",
        "email": "john.newbie@world.com"
    }
    return {**loadersContext, "user": user}
```

There is introduced new test endpoint using http simulator. The http client is created by funtion (see `tests.client.py`). This function overrides `DBDefinitions.ComposeConnectionString` to initialize DBServer on sqlite.

```python
def createGQLClient():

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import DBDefinitions

    def ComposeCString():
        return "sqlite+aiosqlite:///:memory:"
    
    DBDefinitions.ComposeConnectionString = ComposeCString

    import main
    
    client = TestClient(main.app)
    return client
```

This `createGQLClient` function is used in one test (see `tests.test_client.py`).
```python
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
```

This tests adds token to headers thus backend should identify user.

The implemented token based authorization is quite weak but it demonstrates basic principles.
Also this steps still does not used user information for restricting data access.

### Note

The function (see `main.py`)
```python
async def get_context():
    asyncSessionMaker = appcontext.get("asyncSessionMaker", None)
    if asyncSessionMaker is None:
        async with initEngine(app) as cntx:
            pass
        
    from utils.Dataloaders import createLoadersContext
    return createLoadersContext(appcontext["asyncSessionMaker"])
```
has been changed to cover problems with client testing. The change checks if `appcontext["asyncSessionMaker"]` is already avaiable. If not, the initialization is performed.

### Conclusion

To run all tests there is command 

```
pytest --cov-report term-missing --cov=DBDefinitions --cov=GraphTypeDefinitions --cov=utils
```

To run code in development there is 
```
uvicorn main:app --reload
```
