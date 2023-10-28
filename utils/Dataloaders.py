import datetime
from sqlalchemy import select
from functools import cache

from DBDefinitions.eventDBModel import EventModel

def update(destination, source=None, extraValues={}):
    """Updates destination's attributes with source's attributes.
    Attributes with value None are not updated."""
    if source is not None:
        for name in dir(source):
            if name.startswith("_"):
                continue
            value = getattr(source, name)
            if value is not None:
                setattr(destination, name, value)

    for name, value in extraValues.items():
        setattr(destination, name, value)

    return destination


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

        async def insert(self, entity, extra={}):
            newdbrow = DBModel()
            newdbrow = update(newdbrow, entity, extra)
            async with asyncSessionMaker() as session:
                session.add(newdbrow)
                await session.commit()
            return newdbrow
            
        async def update(self, entity, extraValues={}):
            async with asyncSessionMaker() as session:
                statement = baseStatement.filter_by(id=entity.id)
                rows = await session.execute(statement)
                rows = rows.scalars()
                rowToUpdate = next(rows, None)

                if rowToUpdate is None:
                    return None

                dochecks = hasattr(rowToUpdate, 'lastchange')             
                checkpassed = True  
                if (dochecks):
                    if (entity.lastchange != rowToUpdate.lastchange):
                        result = None
                        checkpassed = False                        
                    else:
                        entity.lastchange = datetime.datetime.now()
                if checkpassed:
                    rowToUpdate = update(rowToUpdate, entity, extraValues=extraValues)
                    await session.commit()
                    result = rowToUpdate               
            return result


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
