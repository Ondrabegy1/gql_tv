## Step 2
The source is extended with directory `GraphTypeDefinitions` which has one file `__init__.py`.
Such structure is equivalent of `GraphTypeDefinitions.py` file. 
In future other files can be added, in `__init__.py` imported and by such way extended functionality while code is splited into many files.

`__init__.py` contains structures for "hello world" application on platform GraphQL.
There is `Query` class which contains methods interpreted by strawberry library as possible queries.
Such class is marked in schema construction as root of all queries.
Schema is then used for `GraphQLRouter` instatiation (see main.py). The created object is connected to app (fastapi asgi).

When the program is run, it is possible to open url

`http://localhost:8000/gql`

which serves interface for querying the GraphQL endpoint.
You can try there the query

`{
  hello
}`