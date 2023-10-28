from sqlalchemy import select
from functools import cache

from DBDefinitions.eventDBModel import EventModel

def createLoader(asyncSessionMaker, DBModel):
    class Loader:
        async def load(id):
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


def createContextGetter(asyncSessionMaker):
    async def get_context():
        return {
            "loaders": createLoaders(asyncSessionMaker)
        }        
    return get_context