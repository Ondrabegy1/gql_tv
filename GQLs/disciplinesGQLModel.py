import uuid
import strawberry
import datetime
import typing
import asyncio

from utils.Dataloaders import getLoadersFromInfo

@strawberry.federation.type(
    keys=["id"],
    description="""Entity representing an object""",
)

class DisciplineGQLModel:
    @classmethod
    async def resolve_reference(cls, info: strawberry.types.Info, id: uuid.UUID):
        result = None
        if id is not None: 
            loaders = getLoadersFromInfo(info)
            disciplineloader = loaders.disciplines
            result = await disciplineloader.load(id=id)

        return result
    
    @strawberry.field(description="""Primary key""")
    def id(self) -> uuid.UUID:
        return self.id
    
    @strawberry.field(description="""Name / label of the discipline""")
    def name(self) -> str:
        return self.name
    
    strawberry.field(description="""Timestamp / token""")
    def lastchange(self) -> typing.Optional[datetime.datetime]:
        return self.lastchange
    
    from .permissions import SensitiveInfo
    @strawberry.field(
        permission_classes=[SensitiveInfo],
        description="""This information is hidden from unathorized users""")
    def sensitive_msg(self) -> typing.Optional[str]:
        return "sensitive information"