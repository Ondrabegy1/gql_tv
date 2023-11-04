import uuid
import strawberry
import datetime
import typing
import asyncio

from utils.Dataloaders import getLoadersFromInfo

UserGQLModel = typing.Annotated["UserGQLModel", strawberry.lazy(".userGQLModel")]

@strawberry.federation.type(
    keys=["id"],
    description="""Entity representing an object""",
)
class EventGQLModel:
    @classmethod
    async def resolve_reference(cls, info: strawberry.types.Info, id: uuid.UUID):
        result = None
        if id is not None: 
            loaders = getLoadersFromInfo(info)
            eventloader = loaders.events
            result = await eventloader.load(id=id)

        return result

    @strawberry.field(description="""Primary key""")
    def id(self) -> uuid.UUID:
        return self.id

    @strawberry.field(description="""Name / label of the event""")
    def name(self) -> str:
        return self.name

    @strawberry.field(description="""Moment when the event starts""")
    def startdate(self) -> datetime.datetime:
        return self.startdate

    @strawberry.field(description="""Moment when the event ends""")
    def enddate(self) -> datetime.datetime:
        return self.enddate

    @strawberry.field(description="""Timestamp / token""")
    def lastchange(self) -> typing.Optional[datetime.datetime]:
        return self.lastchange

    from .permissions import SensitiveInfo
    @strawberry.field(
        permission_classes=[SensitiveInfo],
        description="""This information is hidden from unathorized users""")
    def sensitive_msg(self) -> typing.Optional[str]:
        return "sensitive information"

    @strawberry.field(description="""event which contains this event (aka semester of this lesson)""")
    async def master_event(self, info: strawberry.types.Info) -> typing.Union["EventGQLModel", None]:
        if (self.masterevent_id is None):
            result = None
        else:
            result = await EventGQLModel.resolve_reference(info=info, id=self.masterevent_id)
        return result

    @strawberry.field(description="""events which are contained by this event (aka all lessons for the semester)""")
    async def sub_events(self, info: strawberry.types.Info) -> typing.List["EventGQLModel"]:
        loaders = getLoadersFromInfo(info)
        eventloader = loaders.events
        result = await eventloader.filter_by(masterevent_id=self.id)
        return result

    @strawberry.field(description="""users participating on the event""")
    async def users(self, info: strawberry.types.Info) -> typing.List["UserGQLModel"]:
        loaders = getLoadersFromInfo(info)
        eventloader = loaders.eventusers
        rows = await eventloader.filter_by(event_id=self.id)
        userids = (row.user_id for row in rows)
        futureusers = (UserGQLModel.resolve_reference(id=id) for id in userids)
        users = await asyncio.gather(*futureusers)
        return users

import uuid
@strawberry.field(description="""returns and event""")
async def event_by_id(info: strawberry.types.Info, id: uuid.UUID) -> typing.Optional[EventGQLModel]:
    return await EventGQLModel.resolve_reference(info, id)

###################################################################
#
# Mutations
#
###################################################################

@strawberry.input(description="definition of event used for creation")
class EventInsertGQLModel:
    name: str = strawberry.field(description="name / label of event")
    id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    masterevent_id: typing.Optional[uuid.UUID] = strawberry.field(description="ID of master event", default=None)
    startdate: typing.Optional[datetime.datetime] = strawberry.field(description="moment when event starts", default_factory=lambda: datetime.datetime.now())
    enddate: typing.Optional[datetime.datetime] = strawberry.field(description="moment when event ends", default_factory=lambda: datetime.datetime.now() + datetime.timedelta(minutes = 30))

@strawberry.input(description="definition of event used for update")
class EventUpdateGQLModel:
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")
    lastchange: datetime.datetime = strawberry.field(description="timestamp / token for multiuser updates")
    name: typing.Optional[str] = strawberry.field(description="name / label of event", default=None)
    masterevent_id: typing.Optional[uuid.UUID] = strawberry.field(description="ID of master event", default=None)
    startdate: typing.Optional[datetime.datetime] = strawberry.field(description="moment when event starts", default=None)
    enddate: typing.Optional[datetime.datetime] = strawberry.field(description="moment when event ends", default=None)


@strawberry.type(description="result of CUD operation on event")
class EventResultGQLModel:
    id: typing.Optional[uuid.UUID] = None
    msg: str = strawberry.field(description="result of the operation ok / fail", default="")

    @strawberry.field(description="""returns the event""")
    async def event(self, info: strawberry.types.Info) -> EventGQLModel:
        return await EventGQLModel.resolve_reference(info, self.id)

@strawberry.mutation(description="write new event into database")
async def event_insert(self, info: strawberry.types.Info, event: EventInsertGQLModel) -> EventResultGQLModel:
    loader = getLoadersFromInfo(info).events
    row = await loader.insert(event)
    result = EventResultGQLModel()
    result.msg = "ok"
    result.id = row.id
    return result

@strawberry.mutation(description="update the event in database")
async def event_update(self, info: strawberry.types.Info, event: EventUpdateGQLModel) -> EventResultGQLModel:
    loader = getLoadersFromInfo(info).events
    row = await loader.update(event)
    result = EventResultGQLModel()
    result.id = event.id
    if row is None:
        result.msg = "fail"
    else:    
        result.msg = "ok"
    return result
