# gql_evolution

This code is stored with is step by step evolution.
We are going from scratch to full GraphQL (federated) endpoint.

## Technology
FastAPI
Strawberry
SQLAlchemy
Asyncio
AsyncDataLoader

## Initialization
At begin it is stongly recomended to create virtual environment and install all libraries from requirements.txt file.
To run it (in already activated environment) the command

`pip install -r requirements.txt`

should be used.


For each step (aka switching between versions) run

`pip install -r requirements.txt --force`

This enforce full instalation.

## Step 1
This stage contains all code for Swagger endpoint returning (on specific url) JSON {"hello": "world"}.
All appropriate code is in main.py. 
The object app defines asgi application.
Such application can be run with uvicorn

`uvicorn main:app --reload`

`main:app` is location of the python object containing asgi application.
This string has two parts, first one defines the file, second one defines name of object.

When you run this, it is possible to navigate to

http://localhost:8000/hello

This endpoint returns a constant json data.


When you follow url

http://localhost:8000/docs

you can get interface for REST API. In this case OpenAPI standard is used.

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