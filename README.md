## Step 10

This step introduces a capability to use authorization tokens.

### Authentization & Authorization

Authentization is mechanism which ensures that questioner is That Entity (person).

Authorization is mechanism which ensures that questioner has proper right for particular operation (CRUD).

Quite often for authorization is used (http/s request) header item named Authorization.
This header item can have form `Authorization: Bearer ABCDEF`, where `ABCDEF` is token.

When asgi application receives an incomming request, it encodes information about request in data structure. In this case (strawberry) this structure is available at `context["request"]`.

According a token value it is possible to find a user which is owner of the valid token. This process has been encoded into `utils.Dataloaders.py`. There is function `getUserFromInfo`

```python
demouser = {
    "id": "2d9dc5ca-a4a2-11ed-b9df-0242ac120003",
    "name": "John",
    "surname": "Newbie",
    "email": "john.newbie@world.com",
    "roles": [
        {
            "valid": True,
            "group": {
                "id": "2d9dcd22-a4a2-11ed-b9df-0242ac120003",
                "name": "Uni"
            },
            "roletype": {
                "id": "ced46aa4-3217-4fc1-b79d-f6be7d21c6b6",
                "name": "administrátor"
            }
        },
        {
            "valid": True,
            "group": {
                "id": "2d9dcd22-a4a2-11ed-b9df-0242ac120003",
                "name": "Uni"
            },
            "roletype": {
                "id": "ae3f0d74-6159-11ed-b753-0242ac120003",
                "name": "rektor"
            }
        }
    ]
}

def getUserFromInfo(info):
    context = info.context
    #print(list(context.keys()))
    result = context.get("user", None)
    if result is None:
        authorization = context["request"].headers.get("Authorization", None)
        if authorization is not None:
            if 'Bearer ' in authorization:
                token = authorization.split(' ')[1]
                if token == "2d9dc5ca-a4a2-11ed-b9df-0242ac120003":
                    result = demouser
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

### Permissions

Strawberry use permission class to restrict access to field (see https://strawberry.rocks/docs/guides/permissions). The `EventGQLModel` has been extended with a field which can read only authorized user.
```python
    from .permissions import SensitiveInfo
    @strawberry.field(
        permission_classes=[SensitiveInfo],
        description="""This information is hidden from unathorized users""")
    def sensitive_msg(self) -> typing.Optional[str]:
        return "Hidden information"

```

`SensitiveInfo` class is defined in `GraphTypeDefinitions.permissions.py`
```python
from utils.Dataloaders import getUser

class SensitiveInfo(BasePermission):
    message = "User is not allowed to read sensitive info"

    # This method can also be async!
    async def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        user = getUser(info)
        if user is None:
            return False
        if user["id"] == "2d9dc5ca-a4a2-11ed-b9df-0242ac120003":
            return True
        return False
```

This class (its method) returns `True` only for user with particular id. The user is determined in function `getUser` (see above) and describing structure is returned.

The general determination if user would have access to a field could be a quite complicated problem.
Often the access is based on Role based access control (RBAC https://en.wikipedia.org/wiki/Role-based_access_control).

### Short on RBAC
Role based access control is determination if an user has a role which is allowed to perform and operation (CRUD). 
In simple systems are users which have roles and this is enought. 
But for complex systems like an university is also important to check if the user has a role for a group which has right to do CRUD.
As an example we could think about dean and faculty. 
At university are several faculties but dean should operate only on faculty which they are leading.

To cover this problem tables `users`, `groups`, `roles`, `roletypes` and `usergroups` with appropriate relations could be defined. To explain:

- user can be member of many groups
- group can have multiple members
- user can play roles (with roletype) for groups (stored in `roles`)

Let an user is defined as
```json
{
    "id": "2d9dc5ca-a4a2-11ed-b9df-0242ac120003",
    "name": "John",
    "surname": "Newbie",
    "email": "john.newbie@world.com",
    "roles": [
        {
            "valid": true,
            "group": {
                "id": "2d9dcd22-a4a2-11ed-b9df-0242ac120003",
                "name": "Uni"
            },
            "roletype": {
                "id": "ced46aa4-3217-4fc1-b79d-f6be7d21c6b6",
                "name": "administrátor"
            }
        },
        {
            "valid": true,
            "group": {
                "id": "2d9dcd22-a4a2-11ed-b9df-0242ac120003",
                "name": "Uni"
            },
            "roletype": {
                "id": "ae3f0d74-6159-11ed-b753-0242ac120003",
                "name": "rektor"
            }
        }
    ]
}
```

then RBAC could be implemented in class like:

```python
def WhereAuthorized(user, rolesNeeded):
    roleIdsNeeded = list(map(lambda item: item["id"], rolesNeeded))
    print("roleIdsNeeded", roleIdsNeeded)
    # 👇 filtrace roli, ktere maji pozadovanou uroven autorizace
    roletypesFiltered = filter(lambda item: item["roletype"]["id"] in roleIdsNeeded, user["roles"])
    # 👇 odvozeni, pro ktere skupiny ma tazatel patricnou uroven autorizace
    groupsAuthorizedIds = map(lambda item: item["group"]["id"], roletypesFiltered)
    # 👇 konverze na list
    groupsAuthorizedIds = list(groupsAuthorizedIds)
    print("groupsAuthorizedIds", groupsAuthorizedIds)
    return groupsAuthorizedIds

class UserGDPRPermission(BasePermission):
    message = "User has not proper rights"

    async def has_permission(
        self, source, info: strawberry.types.Info, **kwargs
    ) -> bool:
        
        loader = getLoader(info).memberships
        
        # 👇 kdo se pta, a jake role ma
        userAwaitable = getUserFromHeaders({})       
        # 👇 na koho se pta a v jakych skupinach je clenem
        membershipsAwaitable = loader.filter_by(user_id=source.id)
        # 👇 soubeh dotazu
        [user, memberships, *_] = await asyncio.gather(userAwaitable, membershipsAwaitable)
        
        # 👇 jake role jsou nutne pro ziskani informace
        rolesNeeded = [{'id': 'ced46aa4-3217-4fc1-b79d-f6be7d21c6b6', 'name': 'administrátor'}, {'id': 'ae3f0d74-6159-11ed-b753-0242ac120003', 'name': 'rektor'}]      
        # 👇 id skupin, kde ma tazatel pozadovane opravneni
        groupsAuthorizedIds = WhereAuthorized(user, rolesNeeded=rolesNeeded)

        # 👇 id skupin, kde je cil clenem
        userGroupIds = list(map(lambda item: item.group_id, memberships))
        print("userGroupIds", userGroupIds)
        # 👇 filtrace skupin, kde je cil clenem a kde ma tazatel autorizaci
        groupidsIntersection = filter(lambda item: item in groupsAuthorizedIds, userGroupIds)
        # 👇 je zde alespon jeden prunik?
        isAuthorized = next(groupidsIntersection, None) is not None
        print("isAuthorized", isAuthorized)

        print("UserGDPRPermission.user", user)
        print("UserGDPRPermission.source", source.id) # SQLAlchemyModel
        print("UserGDPRPermission.self", self) # GQLModel
        print("UserGDPRPermission.kwargs", kwargs) # resolver parameters
        # return True
        return isAuthorized
```

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
