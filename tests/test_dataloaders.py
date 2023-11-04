import pytest

from .shared import (
    createInfo,
    prepare_in_memory_sqllite
    )

from utils.Dataloaders import getUserFromInfo
@pytest.mark.asyncio
async def test_get_user():
    #asyncSessionMaker = await prepare_in_memory_sqllite()
    info = createInfo(asyncSessionMaker=None)

    user = getUserFromInfo(info)

    assert user is not None
    #assert False