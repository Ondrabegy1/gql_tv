## Step 5

This step introduce a default data import and reading records from database.

### Default data loading
Data import is encapsulated in file `utils.DBFeeder.py` (see function `initDB` there). 
Imported data are stored in `systemdata.json`.
As the type DateTime is stored in json as string, it must be decoded to avoid error messages.
For this task `datetime_parser` function is used.

There is also changed `main.py` file where `initDB` is called when application starts.

### Query from database

For this step only operation **R** (from CRUD) has been chosen.
Reading from database table is implemented in general way in `utils.Dataloaders` with function `load`.


```python
async def load(id):
    async with asyncSessionMaker() as session:
        statement = select(DBModel).filter_by(id=id)
        rows = await session.execute(statement)
        rows = rows.scalars()
        row = next(rows, None)
        return row
```

Function `load` takes `DBModel` and `asyncSessionMaker` variables from context where function has been created. In this particular case it is `createLoader` function.

### Passing session maker to consumers

`EventGQLModel` class with its class method `resolve_reference` is responsible for instatiation of memory variable filled with appropriate values taken from database table.
Question is how we will pass the session maker to this point so this function can communicate with database. 
For such task context is appropriate space.
There is already initialized engine (see `main.py`) stored in `appcontext["asyncSessionMaker"]`.

Strawberry supports passing context variables by `context_getter` parameter.
This parameter is filled with value `get_context` which is function (see below) creating loaders.

```python
def get_context():
    from utils.Dataloaders import createLoadersContext
    return createLoadersContext(appcontext["asyncSessionMaker"])
```

```python
async def createLoadersContext(asyncSessionMaker):
    return {
        "loaders": createLoaders(asyncSessionMaker)
    }
```

In strawberry created context is part of info which should be parameter for methods. As the info is passed, it is possible to retrieve loader.

```python
def getLoadersFromInfo(info):
    context = info.context
    loaders = context["loaders"]
    return loaders
```

Functions `createLoadersContext` and `getLoadersFromInfo` are like sisters.
Having them implemented at same site (file) is quite handy.

### query for attribute value

In this step we use SQLAlchemy models for extracting data from database.
Extracted data are classes not dictionaries, thus appropriate
statements must be changed (see below or `GraphTypeDefinitions.eventGQLModel.py`)

```python
@strawberry.field(description="""Primary key""")
def id(self) -> strawberry.ID:
    return self.id
```

### conclusion

The running GraphQL endpoint could be asked for query

```gql
{
  eventById(id: "08ff1c5d-9891-41f6-a824-fc6272adc189") {
    id
  }
}
```

This event is stored (among others) in `systemdata.json`.

Appropriate response should be

```json
{
  "data": {
    "eventById": {
      "id": "08ff1c5d-9891-41f6-a824-fc6272adc189"
    }
  }
}
```

This step introduced full connection with database and default database content. 
GraphQL endpoint now on query retrieves data from database.