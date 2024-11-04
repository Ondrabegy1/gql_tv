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

    from .eventGQLModel import event_by_id
    event_by_id = event_by_id

@strawberry.type(description="""Type for mutation root""")
class Mutation:
    from .eventGQLModel import event_insert
    event_insert = event_insert

    from .eventGQLModel import event_update
    event_update = event_update

schema = strawberry.federation.Schema(
    query=Query,
    mutation=Mutation
)