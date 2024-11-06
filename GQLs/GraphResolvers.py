from ast import Call
from typing import Coroutine, Callable, Awaitable, Union, List
import uuid
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from uoishelpers.resolvers import (
    create1NGetter,
    createEntityByIdGetter,
    createEntityGetter,
    createInsertResolver,
    createUpdateResolver,
)
from uoishelpers.resolvers import putSingleEntityToDb

from DBs.DBDefinitions import (
    DisciplineModel,
    DisciplineSetModel,
    ResultTemplateModel,
    ResultModel,
    NormModel,
)

# User resolvers
resolveDisciplinesForUser = create1NGetter(
    DisciplineModel, foreignKeyName="user_id"
)
resolveDisciplineSetsForUser = create1NGetter(
    DisciplineSetModel, foreignKeyName="user_id"
)
resolveResultTemplatesForUser = create1NGetter(
    ResultTemplateModel, foreignKeyName="user_id"
)
resolveResultsForUser = create1NGetter(
    ResultModel, foreignKeyName="user_id"
)
resolveNormsForUser = create1NGetter(
    NormModel, foreignKeyName="user_id"
)

# Discipline resolvers
resolveDisciplineById = createEntityByIdGetter(DisciplineModel)
resolveDisciplineAll = createEntityGetter(DisciplineModel)
resolverUpdateDiscipline = createUpdateResolver(DisciplineModel)
resolveInsertDiscipline = createInsertResolver(DisciplineModel)

# DisciplineSet resolvers
resolveDisciplineSetById = createEntityByIdGetter(DisciplineSetModel)
resolveDisciplineSetAll = createEntityGetter(DisciplineSetModel)
resolverUpdateDisciplineSet = createUpdateResolver(DisciplineSetModel)
resolveInsertDisciplineSet = createInsertResolver(DisciplineSetModel)

# ResultTemplate resolvers
resolveResultTemplateById = createEntityByIdGetter(ResultTemplateModel)
resolveResultTemplateAll = createEntityGetter(ResultTemplateModel)
resolverUpdateResultTemplate = createUpdateResolver(ResultTemplateModel)
resolveInsertResultTemplate = createInsertResolver(ResultTemplateModel)

# Result resolvers
resolveResultById = createEntityByIdGetter(ResultModel)
resolveResultAll = createEntityGetter(ResultModel)
resolverUpdateResult = createUpdateResolver(ResultModel)
resolveInsertResult = createInsertResolver(ResultModel)

# Norm resolvers
resolveNormById = createEntityByIdGetter(NormModel)
resolveNormAll = createEntityGetter(NormModel)
resolverUpdateNorm = createUpdateResolver(NormModel)
resolveInsertNorm = createInsertResolver(NormModel)

# Function for searching by three letters
async def resolveDisciplineByThreeLetters(session: AsyncSession, letters: str = "") -> List[DisciplineModel]:
    # If the length of the input is less than 3, return an empty list
    if len(letters) < 3:
        return []
    # Query to search for disciplines whose name contains the letters
    stmt = select(DisciplineModel).where(DisciplineModel.name.like(f"%{letters}%"))
    dbSet = await session.execute(stmt)
    return dbSet.scalars()

async def resolveDisciplineSetByThreeLetters(session: AsyncSession, letters: str = "") -> List[DisciplineSetModel]:
    # If the length of the input is less than 3, return an empty list
    if len(letters) < 3:
        return []
    # Query to search for discipline sets whose name contains the letters
    stmt = select(DisciplineSetModel).where(DisciplineSetModel.name.like(f"%{letters}%"))
    dbSet = await session.execute(stmt)
    return dbSet.scalars()

async def resolveResultTemplateByThreeLetters(session: AsyncSession, letters: str = "") -> List[ResultTemplateModel]:
    # If the length of the input is less than 3, return an empty list
    if len(letters) < 3:
        return []
    # Query to search for result templates whose name contains the letters
    stmt = select(ResultTemplateModel).where(ResultTemplateModel.name.like(f"%{letters}%"))
    dbSet = await session.execute(stmt)
    return dbSet.scalars()

async def resolveResultByThreeLetters(session: AsyncSession, letters: str = "") -> List[ResultModel]:
    # If the length of the input is less than 3, return an empty list
    if len(letters) < 3:
        return []
    # Query to search for results whose note contains the letters
    stmt = select(ResultModel).where(ResultModel.note.like(f"%{letters}%"))
    dbSet = await session.execute(stmt)
    return dbSet.scalars()

async def resolveNormByThreeLetters(session: AsyncSession, letters: str = "") -> List[NormModel]:
    # If the length of the input is less than 3, return an empty list
    if len(letters) < 3:
        return []
    # Query to search for norms whose gender contains the letters
    stmt = select(NormModel).where(NormModel.gender.like(f"%{letters}%"))
    dbSet = await session.execute(stmt)
    return dbSet.scalars()