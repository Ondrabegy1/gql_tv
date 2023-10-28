from sqlalchemy import select
from functools import cache

from DBDefinitions.eventDBModel import EventModel

def createLoader(asyncSessionMaker, DBModel):
    baseStatement = select(DBModel)
    class Loader:
        async def load(self, id):
            async with asyncSessionMaker() as session:
                statement = baseStatement.filter_by(id=id)
                rows = await session.execute(statement)
                rows = rows.scalars()
                row = next(rows, None)
                return row
        
        async def filter_by(self, **kwargs):
            async with asyncSessionMaker() as session:
                statement = baseStatement.filter_by(**kwargs)
                rows = await session.execute(statement)
                rows = rows.scalars()
                return rows

            
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
