from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from GraphTypeDefinitions import schema

app = FastAPI()

print("All initialization is done ")

@app.get('/hello')
def hello():
   return {'hello': 'world'}

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/gql")