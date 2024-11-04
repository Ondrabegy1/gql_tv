import strawberry
import typing
import asyncio

from utils.Dataloaders import getLoadersFromInfo

EventGQLModel = typing.Annotated["EventGQLModel", strawberry.lazy(".eventGQLModel")]

@strawberry.federation.type(extend=True, keys=["id"])
class UserGQLModel:

    id: strawberry.ID = strawberry.federation.field(external=True)

    @classmethod
    async def resolve_reference(cls, id: strawberry.ID):
        result = None
        if id is not None:
            result = UserGQLModel(id=id)
        return result
    
    from .eventGQLModel import EventGQLModel

    @strawberry.field(description="""users participating on the event""")
    async def events(self, info: strawberry.types.Info) -> typing.List["EventGQLModel"]:
        loaders = getLoadersFromInfo(info)
        loader = loaders.eventusers
        rows = await loader.filter_by(user_id=self.id)

        event_ids = map(lambda item: item.event_id, rows)
        futureevents = (EventGQLModel.resolve_reference(info, eventid) for eventid in event_ids)
        events = await asyncio.gather(*futureevents)
        return events
