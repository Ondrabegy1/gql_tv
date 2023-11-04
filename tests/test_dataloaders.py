import pytest
import logging

from .shared import (
    createInfo,
    prepare_in_memory_sqllite
    )

from utils.Dataloaders import getUserFromInfo

@pytest.mark.asyncio
async def test_get_user():
    #asyncSessionMaker = await prepare_in_memory_sqllite()
    info = createInfo(asyncSessionMaker=None, withuser=False)

    user = getUserFromInfo(info)
    logging.info(user)
    assert user is not None
    #assert False