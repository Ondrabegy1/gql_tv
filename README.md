## Step 7

This step will introduce entity relations.

### DBModel

There is `EventGQLModel` which represents an event.
We want to extend this model with possibility to define a master event (school years, semesters, ...). 
The relation between master event and sub events could be defined by foreign key.
Notice last attribute in `EventModel` class below.

```python
class EventModel(BaseModel):
    __tablename__ = "events"

    id = Column(Uuid, primary_key=True, comment="primary key", default=uuid)
    name = Column(String, comment="name / label of the event")

    startdate = Column(DateTime, comment="when the event should start")
    enddate = Column(DateTime, comment="when the event should end")

    masterevent_id = Column(ForeignKey("events.id"), index=True, nullable=True)

```

Because `masterevent_id` is marked as foreign key, database server will test if value here points to existing event (primary key value), if there is event with `id` == `masterevent_id`
Check `systemdata.json`, there is key named `_chunk`. 
Its value allows to control multistage initialization of table (in this case table `events`) to avoid database error. 


```json
{
    "events": [
        {
            "id": "45b2df80-ae0f-11ed-9bd8-0242ac110002" , 
            "name": "Zkouška", 
            "name_en": "Exam", 
            "eventtype_id": "b87d3ff0-8fd4-11ed-a6d4-0242ac110002",
            
            "startdate": "2023-04-19T08:00:00", 
            "enddate": "2023-04-19T09:00:00",
            "_chunk": 2
        },
    ...
    ]
}
```

### GQLModel

Related GQL entity is `EventGQLModel`. 
We want to add here new method `master_event`. This method should return an `EventGQLModel` which has appropriate `id`.

```python
@strawberry.federation.type(
    keys=["id"],
    description="""Entity representing an object""",
)
class EventGQLModel:
    @classmethod
    async def resolve_reference(cls, info: strawberry.types.Info, id: strawberry.ID):
        if id is None: 
            return None

        loaders = getLoadersFromInfo(info)
        eventloader = loaders.events
        result = await eventloader.load(id=id)

        return result

    @strawberry.field(description="""Primary key""")
    def id(self) -> strawberry.ID:
        return self.id

    @strawberry.field(description="""Name / label of the event""")
    def name(self) -> strawberry.ID:
        return self.name

    @strawberry.field(description="""Moment when the event starts""")
    def startdate(self) -> datetime.datetime:
        return self.startdate

    @strawberry.field(description="""Moment when the event ends""")
    def enddate(self) -> datetime.datetime:
        return self.enddate

    @strawberry.field(description="""event which contains this event (aka semester of this lesson)""")
    async def master_event(self, info: strawberry.types.Info) -> typing.Union["EventGQLModel", None]:
        if (self.masterevent_id is None):
            result = None
        else:
            result = await EventGQLModel.resolve_reference(info=info, id=self.masterevent_id)
        return result

```

It is also expected to read all subevents.
In this case we want to retrieve `List` of `EventGQLModel` from database.
All items must have `masterevent_id` equal to current event id.


```python
@strawberry.federation.type(
    keys=["id"],
    description="""Entity representing an object""",
)
class EventGQLModel:

    ...

    @strawberry.field(description="""events which are contained by this event (aka all lessons for the semester)""")
    async def sub_events(self, info: strawberry.types.Info, startdate: datetime.datetime, enddate: datetime.datetime) -> typing.List["EventGQLModel"]:
        loaders = getLoadersFromInfo(info)
        eventloader = loaders.events
        #TODO
        result = await eventloader.filter_by(masterevent_id=self.id)
        return result
```

Loader still does not support method `filter_by`. This must be implemented in file `utils.Dataloaders`.
The `createLoader` function there has now definition below.

```python
def createLoader(asyncSessionMaker, DBModel):
    baseStatement = select(DBModel)
    class Loader:
        async def load(self, id):
            async with asyncSessionMaker() as session:
                statement = baseStatement.filter_by(id=id)
                rows = await session.execute(statement)
                rows = rows.scalars()
                row = next(rows, None)
                return row
        
        async def filter_by(self, **kwargs):
            async with asyncSessionMaker() as session:
                statement = baseStatement.filter_by(**kwargs)
                rows = await session.execute(statement)
                rows = rows.scalars()
                return rows
```
`**kwargs` argument (parameter) represent any structure of named values.
This perfectly fits our needs.

### conclusion

GraphQL endpoint has been exteded with simple relations.

You can open endpoint at 
http://locahost:8000/gql and put query
```gql
{
  eventById(id: "08ff1c5d-9891-41f6-a824-fc6272adc189") {
    id
    name
    startdate
    enddate
    
    masterEvent {
      id
      name
      subEvents {
        id
        name
      }
    }
    
    subEvents {
      id
      name
    }
  }
}
```

The response should be 
```gql
{
  "data": {
    "eventById": {
      "id": "08ff1c5d-9891-41f6-a824-fc6272adc189",
      "name": "2022/23 ZS",
      "startdate": "2022-09-01T00:00:00",
      "enddate": "2023-03-01T00:00:00",
      "masterEvent": {
        "id": "5194663f-11aa-4775-91ed-5f3d79269fed",
        "name": "2022/23",
        "subEvents": [
          {
            "id": "08ff1c5d-9891-41f6-a824-fc6272adc189",
            "name": "2022/23 ZS"
          },
          {
            "id": "0945ad17-3a36-4d33-b849-ad88144415ba",
            "name": "2022/23 LS"
          }
        ]
      },
      "subEvents": []
    }
  }
}
```