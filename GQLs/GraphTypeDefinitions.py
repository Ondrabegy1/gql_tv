from typing import List, Union
import typing
import strawberry as strawberryA
import uuid
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Context manager for creating a session from the info object
@asynccontextmanager
async def withInfo(info):
    asyncSessionMaker = info.context["asyncSessionMaker"]
    async with asyncSessionMaker() as session:
        try:
            yield session
        finally:
            pass

# Define the ResultGQLModel GraphQL type for results, with federation support
@strawberryA.federation.type(extend=True, keys=["id"])
class ResultGQLModel:
    id: strawberryA.ID = strawberryA.federation.field(external=True)
    _value: float

    # Field to get the value of the result
    @strawberryA.field(description="Value of the result")
    def value(self) -> float:
        return self._value

# Resolver function to fetch results from the database with pagination
async def resolveResultAll(session: AsyncSession, skip: int, limit: int) -> List[ResultGQLModel]:
    # Query the database to get results
    result_stmt = select(ResultGQLModel).offset(skip).limit(limit)
    result = await session.execute(result_stmt)
    results = result.scalars().all()
    
    # Return the results as a list of ResultGQLModel instances
    return [ResultGQLModel(id=r.id, _value=r.value) for r in results]

# Define the root query type with a description
@strawberryA.type(description="Type for root queries")
class Query:
    # Define a field to get a paginated list of results
    @strawberryA.field(description="Returns a list of results (paged)")
    async def result_page(
        self, info: strawberryA.types.Info, skip: int = 0, limit: int = 10
    ) -> List[ResultGQLModel]:
        async with withInfo(info) as session:
            result = await resolveResultAll(session, skip, limit)
            return result

# Create the GraphQL schema with the defined query type
schema = strawberryA.federation.Schema(query=Query)