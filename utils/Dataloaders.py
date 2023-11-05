import logging
import datetime
from sqlalchemy import select
from functools import cache

from DBDefinitions import EventModel, EventUserModel

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

        async def execute_select(self, selectstmt):
            async with asyncSessionMaker() as session:
                rows = await session.execute(selectstmt)
                rows = rows.scalars()
                return rows

        async def load(self, id):
            statement = baseStatement.filter_by(id=id)
            rows = self.execute_select(statement)
            row = next(rows, None)
            return row
        
        async def filter_by(self, **kwargs):
            statement = baseStatement.filter_by(**kwargs)
            rows = await self.execute_select(statement)
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

                result = None
                if rowToUpdate is not None:
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

        @property
        @cache
        def eventusers(self):
            return createLoader(asyncSessionMaker, EventUserModel)
        
    return Loaders()


def createLoadersContext(asyncSessionMaker):
    return {
        "loaders": createLoaders(asyncSessionMaker)
    }

def getLoadersFromInfo(info):
    context = info.context
    loaders = context["loaders"]
    return loaders


demouser = {
    "id": "2d9dc5ca-a4a2-11ed-b9df-0242ac120003",
    "name": "John",
    "surname": "Newbie",
    "email": "john.newbie@world.com",
    "roles": [
        {
            "valid": True,
            "group": {
                "id": "2d9dcd22-a4a2-11ed-b9df-0242ac120003",
                "name": "Uni"
            },
            "roletype": {
                "id": "ced46aa4-3217-4fc1-b79d-f6be7d21c6b6",
                "name": "administrátor"
            }
        },
        {
            "valid": True,
            "group": {
                "id": "2d9dcd22-a4a2-11ed-b9df-0242ac120003",
                "name": "Uni"
            },
            "roletype": {
                "id": "ae3f0d74-6159-11ed-b753-0242ac120003",
                "name": "rektor"
            }
        }
    ]
}

def getUserFromInfo(info):
    context = info.context
    #print(list(context.keys()))
    result = context.get("user", None)
    if result is None:
        authorization = context["request"].headers.get("Authorization", None)
        if authorization is not None:
            if 'Bearer ' in authorization:
                token = authorization.split(' ')[1]
                if token == "2d9dc5ca-a4a2-11ed-b9df-0242ac120003":
                    result = demouser
                    context["user"] = result
    logging.debug("getUserFromInfo", result)
    return result


def prepareSelect(model, where: dict):   
    from sqlalchemy import select, and_, or_
    baseStatement = select(model)

    def limitDict(input):
        result = {key: value for key, value in input.items() if value is not None}
        return result
    
    def convertAnd(name, listExpr):
        assert len(listExpr) > 0, "atleast one attribute in And expected"
        results = [convertAny(w) for w in listExpr]
        return and_(*results)

    def convertOr(name, listExpr):
        #print("enter convertOr", listExpr)
        assert len(listExpr) > 0, "atleast one attribute in Or expected"
        results = [convertAny(w) for w in listExpr]
        return or_(*results)

    def convertAttributeOp(name, op, value):
        column = getattr(model, name)
        assert column is not None, f"cannot map {name} to model {model.__tablename__}"
        opMethod = getattr(column, op)
        assert opMethod is not None, f"cannot map {op} to attribute {name} of model {model.__tablename__}"
        return opMethod(value)

    def convertAttribute(attributeName, where):
        woNone = limitDict(where)
        #print("convertAttribute", attributeName, woNone)
        keys = list(woNone.keys())
        assert len(keys) == 1, "convertAttribute: only one attribute in where expected"
        opName = keys[0]
        opValue = woNone[opName]

        ops = {
            "_eq": "__eq__",
            "_lt": "__lt__",
            "_le": "__le__",
            "_gt": "__gt__",
            "_ge": "__ge__",
            "_in": "in_",
            "_like": "like",
            "_ilike": "ilike",
            "_startswith": "startswith",
            "_endswith": "endswith",
        }
        opName = ops[opName]
        #print("op", attributeName, opName, opValue)
        result = convertAttributeOp(attributeName, opName, opValue)
        return result
        
    def convertAny(where):
        
        woNone = limitDict(where)
        #print("convertAny", woNone, flush=True)
        keys = list(woNone.keys())
        #print(keys, flush=True)
        #print(woNone, flush=True)
        assert len(keys) == 1, "convertAny: only one attribute in where expected"
        key = keys[0]
        value = woNone[key]
        
        convertors = {
            "_and": convertAnd,
            "_or": convertOr
        }
        #print("calling", key, "convertor", value, flush=True)
        #print("value is", value, flush=True)
        convertor = convertors.get(key, convertAttribute)

        result = convertor(key, value)
        return result
    
    filterStatement = convertAny(where)
    result = baseStatement.filter(filterStatement)
    return result

def EventSelectByWhere(where):
    import strawberry
    _where = strawberry.asdict(where)    
    return prepareSelect(EventModel, _where)