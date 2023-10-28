from sqlalchemy import select
from functools import cache

from DBDefinitions.eventDBModel import EventModel

def createLoader(asyncSessionMaker, DBModel):
    class Loader:
        async def load(self, id):
            async with asyncSessionMaker() as session:
                statement = select(DBModel).filter_by(id=id)
                rows = await session.execute(statement)
                rows = rows.scalars()
                row = next(rows, None)
                return row
            
    return Loader()

def createLoaders(asyncSessionMaker):
    class Loaders:
        @property
        @cache
        def events(self):
            return createLoader(asyncSessionMaker, EventModel)

    return Loaders()


def createLoadersContext(asyncSessionMaker):
    return {
        "loaders": createLoaders(asyncSessionMaker)
    }

def getLoadersFromInfo(info):
    context = info.context
    loaders = context["loaders"]
    return loaders
