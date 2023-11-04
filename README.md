## Step 11

This step extends GQL federation entities.

### GQL federation

Federation allows to split entites across different endpoints.
It is also possible to extend (aka add new attributes) entities which are defined in different GQL endpoint.

### Entity defined elsewhere

Base entity structure si defined bellow. Notice (and compare with `EventGQLModel`) `resolve_reference` method. If there is responsibility for retrieval information from database this method executes appropriate reading.
Because it is not know where and how the entity is stored, it is impossible to communicate.
Instead there is object created with initial values (keys) filled.

```python
import strawberry

@strawberry.federation.type(extend=True, keys=["id"])
class UserGQLModel:

    id: strawberry.ID = strawberry.federation.field(external=True)

    @classmethod
    async def resolve_reference(cls, id: strawberry.ID):
        result = None
        if id is not None:
            result = UserGQLModel(id=id)
        return result
```

### Database backend

To connect event with user we should think the relation type.
Because naturally event should be visited by multiple users and user can participate on multiple events, the relation type is N:M.
Such relation is in database projected by a special table.


The table in minimal definition has primary key (`id`) and two other attributes.
First one is `user_id`. Because we do not know where `users` and how are stored, there should not be foreignkey. This is reason why we have here just ordinal column typed as `Uuid`.
On the other hand the attribute linking the event should be a foreignkey pointing to `id` of `users` table.
Because we need fast access to both attributes, they are marked as indexed `index=True`.

```python
class EventUserModel(BaseModel):
    __tablename__ = "events_users"

    id = Column(Uuid, primary_key=True, comment="primary key", default=uuid)
    user_id = Column(Uuid, index=True, comment="link to user")
    event_id = Column(ForeignKey("events.id"), index=True, comment="link to event")
```

To "activate" this table definition we must explicitly include the source into imports.
The first should be done by import in `DBDefinitions.__init__`.

Also it could be quite handy to extend `systemdata.json` file with appropriate records.

```json
    "events_users": [
        {
            "id": "89d1e684-ae0f-11ed-9bd8-0242ac110002", 
            "user_id": "89d1e724-ae0f-11ed-9bd8-0242ac110002", 
            "event_id": "45b2df80-ae0f-11ed-9bd8-0242ac110002"
        },
        {
            "id": "89d1f2d2-ae0f-11ed-9bd8-0242ac110002", 
            "user_id": "89d1f34a-ae0f-11ed-9bd8-0242ac110002", 
            "event_id": "45b2df80-ae0f-11ed-9bd8-0242ac110002"
        }
    ]    
```

Do not forget do include appropriate model (`EventUserModel`) in initial DB feeding (`initDB` in `utils.DBFeeder`).

### Loaders

For access to DB loaders are used. 
Because we have extended DB with table `events_users` we should extend loaders also.
Check `utils.Dataloaders`.

```python
def createLoaders(asyncSessionMaker):
    class Loaders:
        @property
        @cache
        def events(self):
            return createLoader(asyncSessionMaker, EventModel)

        @property
        @cache
        def eventusers(self):
            return createLoader(asyncSessionMaker, EventUserModel)
        
    return Loaders()

```

### Entity extension

At this point we have DB prepared. Now both GQL models should be extended.
In the method, loader is accessed then used for filtering records.
Comprehension `(row.event_id for row in rows)` transforms records to ids.
By the way, this kind of comprehension is generator like, it cannot be used (iterated) twice.
`futureevents` are concurently gathered with the help of `events = await asyncio.gather(*futureevents)`. In the end `events` are returned.

```python
@strawberry.federation.type(extend=True, keys=["id"])
class UserGQLModel:

    ...
    from .eventGQLModel import EventGQLModel

    @strawberry.field(description="""users participating on the event""")
    async def events(self, info: strawberry.types.Info) -> typing.List["EventGQLModel"]:
        loaders = getLoadersFromInfo(info)
        loader = loaders.eventusers
        rows = await loader.filter_by(user_id=self.id)

        event_ids = (row.event_id for row in rows)
        futureevents = (EventGQLModel.resolve_reference(info, eventid) for eventid in event_ids)
        events = await asyncio.gather(*futureevents)
        return events
```

The `EventGQLModel` is extended to get event participants. 
Method implementation is very similar to method `UserGQLModel.events`.

```python
@strawberry.federation.type(
    keys=["id"],
    description="""Entity representing an object""",
)
class EventGQLModel:
    ...
    @strawberry.field(description="""users participating on the event""")
    async def users(self, info: strawberry.types.Info) -> typing.List["UserGQLModel"]:
        loaders = getLoadersFromInfo(info)
        loader = loaders.eventusers
        rows = await loader.filter_by(event_id=self.id)

        userids = (row.user_id for row in rows)
        futureusers = (UserGQLModel.resolve_reference(id=id) for id in userids)
        users = await asyncio.gather(*futureusers)
        return users
```

### Test coverage

It is important that code (even newly added) is covered by tests.
Bellow is created test (by calling `createFrontendQuery`) for `EventGQLModel.users` attribute coverage.

```python
test_query_event_with_users = createFrontendQuery(
    query="""
        query($id: UUID!) {
            result: eventById(id: $id) {
                id
                name
                lastchange
                users { 
                    id 
                    events {
                        id
                        name
                    }
                }
            }
        }""",
    variables={
        "id": "45b2df80-ae0f-11ed-9bd8-0242ac110002",
    },
    asserts = [
        lambda data: runAssert(data.get("result", None) is not None, "expected data.result"),
        lambda data: runAssert(data["result"].get("users", None) is not None, "expected not None ")
    ]
)
```

It is also needed to test attribute `events` for entity `UserGQLModel`. 
Because we have not a method to query for `UserGQLModel`, we should use another approach.
This is demonstrated below. 
There is used a special query for `_entities`.

```python
test_query_user_with_events = createFrontendQuery(
    query="""
        query($id: UUID!) { 
            result: _entities(representations: [{ __typename: "UserGQLModel", id: $id }]) {
                ...on UserGQLModel { 
                    id 
                    events {
                        id
                        name
                    }
                }
            }
        }""",
    variables={
        "id": "89d1e724-ae0f-11ed-9bd8-0242ac110002",
    },
    asserts = [
        lambda data: runAssert(data.get("result", None) is not None, "expected data.result")
    ]
)
```

### Extra on logging

In the code simple `print` statement has been replaced with `logging.info`, `logging.debug`, ...
Check `main.py`, look for

```python
logging.basicConfig(format='%(asctime)s\t%(levelname)s:\t%(message)s', level=logging.DEBUG, datefmt='%Y-%m-%dT%I:%M:%S')
```

### Conclusion

The entity from other federation member (`UserGQLModel`) has been extended and entity `EventGQLModel` has method which returns a `List[UserGQLModel]`.


```
uvicorn main:app --reload
```

The query bellow returns a link to other federation members

```gql
{
    result: eventById(id: "45b2df80-ae0f-11ed-9bd8-0242ac110002") {
        id
        name
        lastchange
        users { 
            id 
            events {
                id
                name
            }
        }
    }
}
```

There is little tuning to get high pytest code coverage (tests added).
To run all tests there is command 

```
pytest --cov-report term-missing --cov=DBDefinitions --cov=GraphTypeDefinitions --cov=utils
```

to see all logs
```
pytest --cov-report term-missing --cov=DBDefinitions --cov=GraphTypeDefinitions --cov=utils --log-cli-level=INFO
```

To run code in development there is 
```
uvicorn main:app --log-config=log_conf.yaml --reload
```
