from typing import List, Union
import typing
import strawberry as strawberryA
import uuid
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

@asynccontextmanager
async def withInfo(info):
    asyncSessionMaker = info.context["asyncSessionMaker"]
    async with asyncSessionMaker() as session:
        try:
            yield session
        finally:
            pass

@strawberryA.federation.type(extend=True, keys=["id"])
class ResultGQLModel:
    id: strawberryA.ID = strawberryA.federation.field(external=True)
    _value: float

    @strawberryA.field(description="Hodnota výsledku")
    def value(self) -> float:
        return self._value

async def resolveResultAll(session: AsyncSession, skip: int, limit: int) -> List[ResultGQLModel]:
    # Dotaz na databázi pro získání výsledků
    result_stmt = select(ResultGQLModel).offset(skip).limit(limit)
    result = await session.execute(result_stmt)
    results = result.scalars().all()
    
    return [ResultGQLModel(id=r.id, _value=r.value) for r in results]

@strawberryA.type(description="Typ pro root dotazy")
class Query:
    @strawberryA.field(description="Vrátí seznam výsledků (paged)")
    async def result_page(
        self, info: strawberryA.types.Info, skip: int = 0, limit: int = 10
    ) -> List[ResultGQLModel]:
        async with withInfo(info) as session:
            result = await resolveResultAll(session, skip, limit)
            return result

schema = strawberryA.federation.Schema(query=Query)