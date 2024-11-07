import logging
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from .baseDBModel import BaseModel
from .DBDefinitions import DisciplineModel

# Performs necessary operations and returns an asynchronous SessionMaker.

async def startEngine(connectionstring, makeDrop=False, makeUp=True):
    
    # Create an asynchronous engine for database connection
    asyncEngine = create_async_engine(connectionstring)

    # Asynchronous context for database operations
    async with asyncEngine.begin() as conn:
        if makeDrop:
            await conn.run_sync(BaseModel.metadata.drop_all)
            logging.info("BaseModel.metadata.drop_all finished")
        if makeUp:
            try:
                await conn.run_sync(BaseModel.metadata.create_all)
                logging.info("BaseModel.metadata.create_all finished")
            except sqlalchemy.exc.NoReferencedTableError as e:
                logging.info(f"{e} : Unable to automatically create tables")
                return None

    # Create an asynchronous session maker
    async_sessionMaker = sessionmaker(
        asyncEngine, expire_on_commit=False, class_=AsyncSession
    )
    return async_sessionMaker

import os

# Derives the connection string from environment variables or Docker Envs.

# Returns: connectionstring (str): Connection string for database connection.

def ComposeConnectionString():
    
    # Get database information from environment
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "example")
    database = os.environ.get("POSTGRES_DB", "data")
    hostWithPort = os.environ.get("POSTGRES_HOST", "localhost:5432")

    # Build the connection string
    driver = "postgresql+asyncpg"  # "postgresql+psycopg2"
    connectionstring = f"{driver}://{user}:{password}@{hostWithPort}/{database}"

    logging.info(f"CString {database} at {hostWithPort}")
    return connectionstring