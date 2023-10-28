from contextlib import asynccontextmanager
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from GraphTypeDefinitions import schema

appcontext = {}
@asynccontextmanager
async def initEngine(app: FastAPI):

    from DBDefinitions import startEngine, ComposeConnectionString

    connectionstring = ComposeConnectionString()

    asyncSessionMaker = await startEngine(
        connectionstring=connectionstring,
        makeDrop=True,
        makeUp=True
    )

    appcontext["asyncSessionMaker"] = asyncSessionMaker
    print("engine started", flush=True)
    yield


app = FastAPI(lifespan=initEngine)

print("All initialization is done ")

@app.get('/hello')
def hello():
   return {'hello': 'world'}

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/gql")