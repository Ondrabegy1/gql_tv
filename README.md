## Step 8

This step will introduce **C** and **U** operations (from CRUD).

### Create

To create a new `EventGQLModel` and / or `EventModel` (in database) the incomming request should contain event definition.
For this a class must be added (file `DBDefinitions.eventDBModel`).

```python
@strawberry.input(description="definition of event used for creation")
class EventInsertGQLModel:
    name: str = strawberry.field(description="name / label of event")
    id: typing.Optional[strawberry.ID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    masterevent_id: typing.Optional[strawberry.ID] = strawberry.field(description="ID of master event", default=None)
    startdate: typing.Optional[datetime.datetime] = strawberry.field(description="moment when event starts", default_factory=lambda: datetime.datetime.now())
    enddate: typing.Optional[datetime.datetime] = strawberry.field(description="moment when event ends", default_factory=lambda: datetime.datetime.now() + datetime.timedelta(minutes = 30))

```

This structure is just a GraphQL (we are using strawberry) input parameter.
This paramater will be used in function which will create a new database record.
GraphQL has named such functions as **mutations**.

When a change has been done, the client should get response containing a message that operation has been finished or failed. Thus we need an extra structure for this result.

```python
@strawberry.type(description="result of CUD operation on event")
class EventResultGQLModel:
    id: typing.Optional[strawberry.ID] = None
    msg: str = strawberry.field(description="result of the operation ok / fail", default="")

    @strawberry.field(description="""returns the event""")
    async def event(self, info: strawberry.types.Info) -> EventGQLModel:
        return await EventGQLModel.resolve_reference(info, self.id)

```

Now we can define a function for mutation.

```python
@strawberry.mutation(description="write a new event into database")
async def event_insert(self, info: strawberry.types.Info, event: EventInsertGQLModel) -> EventResultGQLModel:
    loader = getLoadersFromInfo(info).events
    row = await loader.insert(event)
    result = EventResultGQLModel()
    result.msg = "ok"
    result.id = row.id
    return result
```

Class `Loader` miss the method `insert`, so we must extend it. See file `utils.Dataloaders.py`
```python
def createLoader(asyncSessionMaker, DBModel):
    baseStatement = select(DBModel)
    class Loader:
        ...
        async def insert(self, entity, extra={}):
            newdbrow = DBModel()
            newdbrow = update(newdbrow, entity, extra)
            async with asyncSessionMaker() as session:
                session.add(newdbrow)
                await session.commit()
            return newdbrow
```

Notice call of function `update`. 
This is function which can transfer attributes from entity (strawberry input type) to DBModel. 
There is also `extra` parameter which allows to ovewrite some attributes.

```python
def update(destination, source=None, extraValues={}):
    """Updates destination's attributes with source's attributes.
    Attributes with value None are not updated."""
    if source is not None:
        for name in dir(source):
            if name.startswith("_"):
                continue
            value = getattr(source, name)
            if value is not None:
                setattr(destination, name, value)

    for name, value in extraValues.items():
        setattr(destination, name, value)

    return destination
```

All mutations are encapsulated into single type and exposed as part of schema
`Mutation` class from file `GraphTypeDefinitions.__init__.py`
```python
@strawberry.type(description="""Type for mutation root""")
class Mutation:
    from .eventGQLModel import event_insert
    event_insert = event_insert
```

Schema creation should be changed (see `GraphTypeDefinitions.__init__.py` file):
```python
schema = strawberry.federation.Schema(
    query=Query,
    mutation=Mutation
)
```

### update

Update is another operation on `EventGQLModel` (`EventModel`). 
Result of this operation must change database.
For this operation we must know primary key value.
It identifies entity which is object of this operation.
Primary key is **mandatory** value.
It differs from creation so we need another input structure.

There is also problem with concurrent work (multiple users).
To avoid overwritting changes done by other user, the token must be used.
The token is retrieved from database and during update operation this token is checked.
If the value is same as in database, the record has not been changed.
Otherwise, the operation should not be finished as someone changed record meanwhile.

Such token can be easily implemented by timestamp.
This means that `EventModel` must be extended.
`lastchange` is new attribute which is generated at client side.
Try to find serverside solution.

```python
class EventModel(BaseModel):
    __tablename__ = "events"

    id = Column(Uuid, primary_key=True, comment="primary key", default=uuid)
    name = Column(String, comment="name / label of the event")

    startdate = Column(DateTime, comment="when the event should start")
    enddate = Column(DateTime, comment="when the event should end")

    masterevent_id = Column(
        ForeignKey("events.id"), index=True, nullable=True,
        comment="event which owns this event")

    lastchange = Column(DateTime, default=datetime.datetime.now)
```

To get value of `lastchange` new attribute to `EventGQLModel` must be added

```python
    @strawberry.field(description="""Timestamp / token""")
    def lastchange(self) -> typing.Optional[datetime.datetime]:
        return self.lastchange
```

At this stage it is possible to introduce data structure describing update operation.

```python
@strawberry.input(description="definition of event used for update")
class EventUpdateGQLModel:
    id: strawberry.ID = strawberry.field(description="primary key (UUID), identifies object of operation")
    lastchange: datetime.datetime = strawberry.field(description="timestamp / token for multiuser updates")
    name: typing.Optional[str] = strawberry.field(description="name / label of event", default=None)
    masterevent_id: typing.Optional[strawberry.ID] = strawberry.field(description="ID of master event", default=None)
    startdate: typing.Optional[datetime.datetime] = strawberry.field(description="moment when event starts", default=None)
    enddate: typing.Optional[datetime.datetime] = strawberry.field(description="moment when event ends", default=None)

```

Result of update operation can be same as for operation insert (create).
Now we need new mutation `event_update` 

```python
@strawberry.mutation(description="update the event in database")
async def event_update(self, info: strawberry.types.Info, event: EventUpdateGQLModel) -> EventResultGQLModel:
    loader = getLoadersFromInfo(info).events
    row = await loader.update(event)
    result = EventResultGQLModel()
    result.id = event.id
    if row is None:
        result.msg = "fail"
    else:    
        result.msg = "ok"
    return result
```

We miss method `update` on loader (defined in file `utils.Dataloaders.py`).
Notice the test of opration's result.
If it is `None`, operation failed as timestamp was not different.

There must be loaded entity from database, if it does not exists, the operation failed (bad value of primary key).
If there is attribute `lastchange`, it has timestamp.
This timestamp must the updater know.
If the value is different, someone overwritten record. 
Operation failed.
If all checks have passed, the update can be performed.
Also timestamp must be changed to protect unwanted changes (new token).


```python
def createLoader(asyncSessionMaker, DBModel):
    baseStatement = select(DBModel)
    class Loader:
        ...
        async def update(self, entity, extraValues={}):
            async with asyncSessionMaker() as session:
                statement = baseStatement.filter_by(id=entity.id)
                rows = await session.execute(statement)
                rows = rows.scalars()
                rowToUpdate = next(rows, None)

                if rowToUpdate is None:
                    return None

                dochecks = hasattr(rowToUpdate, 'lastchange')             
                checkpassed = True  
                if (dochecks):
                    if (entity.lastchange != rowToUpdate.lastchange):
                        result = None
                        checkpassed = False                        
                    else:
                        entity.lastchange = datetime.datetime.now()
                if checkpassed:
                    rowToUpdate = update(rowToUpdate, entity, extraValues=extraValues)
                    await session.commit()
                    result = rowToUpdate               
            return result
```

Do not forget to include this new mutation in `Mutation` class (file `GraphTypeDefinitions.__init__.py`).
```python
@strawberry.type(description="""Type for mutation root""")
class Mutation:
    from .eventGQLModel import event_insert
    event_insert = event_insert

    from .eventGQLModel import event_update
    event_update = event_update
```

### conclusion

From now, if the code is running, it is possible to open
http://localhost:8000/gql

and send mutation

```gql
mutation {
  eventInsert(
    event: {id: "bbedf480-3e1d-435c-b994-1a4991e0b87b", name: "new event"}
  ) {
    msg
    id
    event {
      id
      name
      lastchange
    }
  }
}
```

Response should be
```gql
{
  "data": {
    "eventInsert": {
      "msg": "ok",
      "id": "bbedf480-3e1d-435c-b994-1a4991e0b87b",
      "event": {
        "id": "bbedf480-3e1d-435c-b994-1a4991e0b87b",
        "name": "new event",
        "lastchange": "2023-10-28T21:48:15.138121"
      }
    }
  }
}
```

Notice that we enforce primary key value. If you post this mutation second time, database would throw an error

Response for second (same) mutation:

```gql
{
  "data": null,
  "errors": [
    {
      "message": "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.UniqueViolationError'>: duplicate key value violates unique constraint \"events_pkey\"\nDETAIL:  Key (id)=(bbedf480-3e1d-435c-b994-1a4991e0b87b) already exists.\n[SQL: INSERT INTO events (id, name, startdate, enddate, masterevent_id, lastchange) VALUES ($1::UUID, $2::VARCHAR, $3::TIMESTAMP WITHOUT TIME ZONE, $4::TIMESTAMP WITHOUT TIME ZONE, $5::UUID, $6::TIMESTAMP WITHOUT TIME ZONE)]\n[parameters: ('bbedf480-3e1d-435c-b994-1a4991e0b87b', 'new event', datetime.datetime(2023, 10, 28, 21, 46, 59, 296182), datetime.datetime(2023, 10, 28, 22, 16, 59, 296182), None, datetime.datetime(2023, 10, 28, 21, 48, 45, 57987))]\n(Background on this error at: https://sqlalche.me/e/20/gkpj)",
      "locations": [
        {
          "line": 2,
          "column": 3
        }
      ],
      "path": [
        "eventInsert"
      ]
    }
  ]
}
```

It is possible to change name of the newly created event.
**The `lastchange` must be set to proper value.**

```gql
mutation {
  eventUpdate(
    event: {
      id: "bbedf480-3e1d-435c-b994-1a4991e0b87b", 
      lastchange: "2023-10-28 21:48:15.138121", 
      name: "new event X"
    }
  ) {
    msg
    id
    event {
      id
      name
      lastchange
    }
  }
}
```

Response should look like
```json
{
  "data": {
    "eventUpdate": {
      "msg": "ok",
      "id": "bbedf480-3e1d-435c-b994-1a4991e0b87b",
      "event": {
        "id": "bbedf480-3e1d-435c-b994-1a4991e0b87b",
        "name": "new event X",
        "lastchange": "2023-10-28T21:50:16.663328"
      }
    }
  }
}
```