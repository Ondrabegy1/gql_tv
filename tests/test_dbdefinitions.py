import sqlalchemy
from sqlalchemy import select
import sys
import asyncio

# # setting path
#sys.path.append("..")

import pytest

# from ..uoishelpers.uuid import UUIDColumn

from .shared import prepare_demodata, prepare_in_memory_sqllite, get_demodata
from DBs import BaseModel, EventModel


@pytest.mark.asyncio
async def test_load_demo_data():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    #data = get_demodata()

    


from DBs import ComposeConnectionString


def test_connection_string():
    connectionString = ComposeConnectionString()

    assert "://" in connectionString
    assert "@" in connectionString


from DBs import startEngine


@pytest.mark.asyncio
async def test_table_start_engine():
    connectionString = "sqlite+aiosqlite:///:memory:"
    async_session_maker = await startEngine(
        connectionString, makeDrop=True, makeUp=True
    )

    assert async_session_maker is not None


from utils.DBFeeder import initDB


@pytest.mark.asyncio
async def test_initDB():
    connectionString = "sqlite+aiosqlite:///:memory:"
    async_session_maker = await startEngine(
        connectionString, makeDrop=True, makeUp=True
    )

    assert async_session_maker is not None
    await initDB(async_session_maker)
