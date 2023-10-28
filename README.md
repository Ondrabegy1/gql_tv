## Step 3
The `eventGQLModel.py` is added. It has class `EventGQLModel` which represents (unfinished) Event entity.
Also there is function `event_by_id` which calls `EventGQLModel.resolve_reference` and creates the appropriate object in memory.
In this case it is dictionary.

`EventGQLModel.resolve_reference` is the point where entity should be loaded from persistent storage (database?).

Notice method `EventGQLModel.id` which is attribute getter. It extracts `id` from the object (dictionary) `self["id"]`.

Function `event_by_id` is imported in `__init__.py` and linked as a method of class `Query`.
By this way the GraphQL endpoint is extended.

When application is running, go to url

http://localhost:8000/gql

and try the query

`
{
  eventById(id: "1231321") {
    id
  }
}
`