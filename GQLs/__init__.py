import strawberry

# Define the root query type with a description
@strawberry.type(description="Type for query root")
class Query:
    # Define a field for the query root with a description
    @strawberry.field(
        description="Returns hello world"
    )
    async def hello(
        self,
        info: strawberry.types.Info,
    ) -> str:
        # Return a simple string as the query response
        return "hello world"

# Define the root mutation type with a description
@strawberry.type(description="Type for mutation root")
class Mutation:
    # Define a field for the mutation root with a description
    @strawberry.field(
        description="Returns hello world"
    )
    async def hello(
        self,
        info: strawberry.types.Info,
    ) -> str:
        # Return a simple string as the mutation response
        return "hello world"

# Create the GraphQL schema with the defined query and mutation types
schema = strawberry.federation.Schema(
    query=Query,
    mutation=Mutation
)