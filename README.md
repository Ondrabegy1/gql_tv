## Step 6

This step will extend DBModel and GQLModel.

### DBModel

There is `EventGQLModel` which represents an event.
It is possible to store in database only primary key (id) and name of the event.
But events have their starts and ends. 
This should be enabled by addition of other attributes.

```python
class EventModel(BaseModel):
    __tablename__ = "events"

    id = Column(Uuid, primary_key=True, comment="primary key", default=uuid)
    name = Column(String, comment="name / label of the event")

    startdate = Column(DateTime, comment="when the event should start")
    enddate = Column(DateTime, comment="when the event should end")
```

Other relevant code should adapt this change

### GQLModel

If we want (and we should) to allow reading from database, we have to refactor `EventGQLModel`. 

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
```

### conclusion

Now we can query GraphQL endpoint for all implemented attributes.

You can open endpoint at 
http://locahost:8000/gql and put query
```gql
{
  eventById(id: "08ff1c5d-9891-41f6-a824-fc6272adc189") {
    id
    name
    startdate
    enddate
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
      "enddate": "2023-03-01T00:00:00"
    }
  }
}
```