import strawberry


@strawberry.federation.type(
    keys=["id"],
    description="""Entity representing an object""",
)
class EventGQLModel:
    @classmethod
    async def resolve_reference(cls, info: strawberry.types.Info, id: strawberry.ID):
        if id is None: 
            return None

        result = {"id": id}

        return result

    @strawberry.field(description="""Primary key""")
    def id(self) -> strawberry.ID:
        return self["id"]


@strawberry.field(description="""returns and event""")
async def event_by_id(info: strawberry.types.Info, id: strawberry.ID) -> EventGQLModel:
    return await EventGQLModel.resolve_reference(info, id)