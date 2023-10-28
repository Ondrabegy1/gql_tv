import strawberry

@strawberry.type(description="""Type for query root""")
class Query:
    @strawberry.field(
        description="""Returns hello world"""
        )
    async def hello(
        self,
        info: strawberry.types.Info,
    ) -> str:
        return "hello world"


schema = strawberry.federation.Schema(
    query=Query
)