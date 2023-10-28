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

    from utils.DBFeeder import initDB
    await initDB(asyncSessionMaker)

    print("data (if any) imported", flush=True)
    yield


app = FastAPI(lifespan=initEngine)

print("All initialization is done ")

@app.get('/hello')
def hello():
   return {'hello': 'world'}


def get_context():
    from utils.Dataloaders import createLoadersContext
    return createLoadersContext(appcontext["asyncSessionMaker"])

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context
)

app.include_router(graphql_app, prefix="/gql")