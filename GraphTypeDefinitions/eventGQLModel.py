import strawberry
import datetime

from utils.Dataloaders import getLoadersFromInfo

@strawberry.federation.type(
    keys=["id"],
    description="""Entity representing an object""",
)
class EventGQLModel:
    @classmethod
    async def resolve_reference(cls, info: strawberry.types.Info, id: strawberry.ID):
        if id is None: 
            return None

        loaders = getLoadersFromInfo(info)
        eventloader = loaders.events
        result = await eventloader.load(id=id)

        return result

    @strawberry.field(description="""Primary key""")
    def id(self) -> strawberry.ID:
        return self.id

    @strawberry.field(description="""Name / label of the event""")
    def name(self) -> strawberry.ID:
        return self.name

    @strawberry.field(description="""Moment when the event starts""")
    def startdate(self) -> datetime.datetime:
        return self.startdate

    @strawberry.field(description="""Moment when the event ends""")
    def enddate(self) -> datetime.datetime:
        return self.enddate


@strawberry.field(description="""returns and event""")
async def event_by_id(info: strawberry.types.Info, id: strawberry.ID) -> EventGQLModel:
    return await EventGQLModel.resolve_reference(info, id)