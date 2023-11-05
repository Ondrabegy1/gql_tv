import typing
import sys
import strawberry
from dataclasses import dataclass
import datetime

inputTypeGQLMapper = {}

def createInputs(cls):
    clsname = cls.__name__
    whereName = clsname + "_where"
    orName = clsname + "_or"
    andName = clsname + "_and"

    fieldNames = [field_name for field_name in cls.__annotations__]
    opNames = [clsname + "_" + field_name for field_name in fieldNames]
    types = [field for field in cls.__annotations__.values()]

    def createCustomInput(field, name, baseType = str):
        result = inputTypeGQLMapper.get(baseType, None)
        if result is None:
            result = type(name, (object,), {})
            result.__annotations__ = {
                op: typing.Optional[baseType] for op in ["_eq", "_le", "_lt", "_ge", "_gt"]
            }
            for op in ["_eq", "_le", "_lt", "_ge", "_gt"]:
                setattr(result, op, strawberry.field(name=op, description="operation for select.filter() method", default=None))           
            result = strawberry.input(result, description=f"Expression on attribute '{field}'. Only one constrain allowed.")
        return   result

    inputTypes = [
        createCustomInput(field, name, baseType)
        for field, name, baseType in zip(fieldNames, opNames, types)
    ]
    
    inputTypesDict = {
        fieldName: typing.Optional[inputType]
        for fieldName, inputType in zip(fieldNames, inputTypes)
    }

    #print("inputTypesDict")
    #print(inputTypesDict)

    def createOr():
        result = type(orName, (object,), {})
        anotations = {
            "_and": typing.Optional[typing.List[andName]],
            **inputTypesDict
        }
        result.__annotations__ = anotations
        for op in anotations.keys():
            setattr(result, op, 
                strawberry.field(name=op, description="Filter method", default=None)
            )
        return result  
        
    orOp = strawberry.input(createOr(), description=f"Or operator definition on {clsname}")
    #print("orOp")
    #print(orOp)

    def createAnd():
        result = type(andName, (object,), {})
        anotations = {
            "_or": typing.Optional[typing.List[orName]],
            **inputTypesDict
        }
        result.__annotations__ = anotations
        for op in anotations.keys():
            setattr(result, op, 
                strawberry.field(name=op, description="Filter method", default=None)
            )
        return result

    andOp = strawberry.input(createAnd(), description=f"And operator definition on {clsname}")
    #print("andOp")
    #print(andOp)

    def createWhereOp():
        result = type(whereName, (object,), {})
        anotations = {
            "_or": typing.Optional[typing.List[orOp]],
            "_and": typing.Optional[typing.List[andOp]],
            **inputTypesDict
        }
        result.__annotations__ = anotations
        for op in anotations.keys():
            setattr(result, op, 
                strawberry.field(name=op, description="Filter method", default=None)
            )
            
        return result  

    whereOp = strawberry.input(createWhereOp(), description=f"Operators definition on {clsname}")
    #print("topOp")
    #print(topOp)
       
    ####################################
    # make all ops global in this module
    ####################################
    result = [whereOp, andOp, orOp, *inputTypes]
    this = sys.modules[__name__]
    for r in result:
        setattr(this, r.__name__, r)

    #return [topOp, andOp, orOp, *inputTypes]
    return whereOp
    #return inputTypes

@strawberry.input(description="Str filter methods, only one constrain allowed")
class StrFilter:
    _eq: typing.Optional[str] = strawberry.field(name="_eq", description="operation for select.filter() method", default=None)
    _le: typing.Optional[str] = strawberry.field(name="_le", description="operation for select.filter() method", default=None)
    _lt: typing.Optional[str] = strawberry.field(name="_lt", description="operation for select.filter() method", default=None)
    _ge: typing.Optional[str] = strawberry.field(name="_ge", description="operation for select.filter() method", default=None)
    _gt: typing.Optional[str] = strawberry.field(name="_gt", description="operation for select.filter() method", default=None)
    _like: typing.Optional[str] = strawberry.field(name="_like", description="operation for select.filter() method", default=None)
    _ilike: typing.Optional[str] = strawberry.field(name="_ilike", description="operation for select.filter() method", default=None)
    _startswith: typing.Optional[str] = strawberry.field(name="_startswith", description="operation for select.filter() method", default=None)
    _endswith: typing.Optional[str] = strawberry.field(name="_endswith", description="operation for select.filter() method", default=None)

@strawberry.input(description="Datetime filter methods, only one constrain allowed")
class DatetimeFilter:
    _eq: typing.Optional[datetime.datetime] = strawberry.field(name="_eq", description="operation for select.filter() method", default=None)
    _le: typing.Optional[datetime.datetime] = strawberry.field(name="_le", description="operation for select.filter() method", default=None)
    _lt: typing.Optional[datetime.datetime] = strawberry.field(name="_lt", description="operation for select.filter() method", default=None)
    _ge: typing.Optional[datetime.datetime] = strawberry.field(name="_ge", description="operation for select.filter() method", default=None)
    _gt: typing.Optional[datetime.datetime] = strawberry.field(name="_gt", description="operation for select.filter() method", default=None)

@strawberry.input(description="Integer filter methods, only one constrain allowed")
class IntFilter:
    _eq: typing.Optional[int] = strawberry.field(name="_eq", description="operation for select.filter() method", default=None)
    _le: typing.Optional[int] = strawberry.field(name="_le", description="operation for select.filter() method", default=None)
    _lt: typing.Optional[int] = strawberry.field(name="_lt", description="operation for select.filter() method", default=None)
    _ge: typing.Optional[int] = strawberry.field(name="_ge", description="operation for select.filter() method", default=None)
    _gt: typing.Optional[int] = strawberry.field(name="_gt", description="operation for select.filter() method", default=None)
    _in: typing.Optional[typing.List[int]] = strawberry.field(name="_in", description="operation for select.filter() method", default=None)

@strawberry.input(description="Integer filter methods, only one constrain allowed")
class BoolFilter:
    _eq: typing.Optional[bool] = strawberry.field(name="_eq", description="operation for select.filter() method", default=None)

import uuid
uuid.UUID
@strawberry.input(description="Integer filter methods, only one constrain allowed")
class UuidFilter:
    _eq: typing.Optional[uuid.UUID] = strawberry.field(name="_eq", description="operation for select.filter() method", default=None)
    _in: typing.Optional[typing.List[uuid.UUID]] = strawberry.field(name="_in", description="operation for select.filter() method", default=None)

inputTypeGQLMapper[uuid.UUID] = UuidFilter
inputTypeGQLMapper[int] = IntFilter
inputTypeGQLMapper[str] = StrFilter
inputTypeGQLMapper[datetime.datetime] = DatetimeFilter
inputTypeGQLMapper[bool] = BoolFilter