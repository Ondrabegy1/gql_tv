import logging
logging.basicConfig(format='%(asctime)s\t%(levelname)s:\t%(message)s', level=logging.DEBUG, datefmt='%Y-%m-%dT%I:%M:%S')

from contextlib import asynccontextmanager
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from GQLs import schema

appcontext = {}
@asynccontextmanager
async def initEngine(app: FastAPI):

    from DBs import startEngine, ComposeConnectionString

    connectionstring = ComposeConnectionString()

    asyncSessionMaker = await startEngine(
        connectionstring=connectionstring,
        makeDrop=True,
        makeUp=True
    )

    appcontext["asyncSessionMaker"] = asyncSessionMaker

    logging.info("engine started")

    from utils.DBFeeder import initDB
    await initDB(asyncSessionMaker)

    logging.info("data (if any) imported")
    yield


app = FastAPI(lifespan=initEngine)

logging.info("All initialization is done ")

@app.get('/hello')
def hello():
   return {'hello': 'world'}


async def get_context():
    asyncSessionMaker = appcontext.get("asyncSessionMaker", None)
    if asyncSessionMaker is None:
        async with initEngine(app) as cntx:
            pass
        
    from utils.Dataloaders import createLoadersContext
    return createLoadersContext(appcontext["asyncSessionMaker"])

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context
)

app.include_router(graphql_app, prefix="/gql")

