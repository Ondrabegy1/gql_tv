import logging
import typing
import strawberry
from strawberry.permission import BasePermission
from strawberry.types import Info

from utils.Dataloaders import getUserFromInfo

class SensitiveInfo(BasePermission):
    message = "User is not allowed to read sensitive info"

    # This method can also be async!
    async def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        user = getUserFromInfo(info)
        #print("SensitiveInfo test for", user)
        result = False
        if user is not None:
            if user["id"] == "2d9dc5ca-a4a2-11ed-b9df-0242ac120003":
                result = True
        logging.info(f"{user} attempt to get sensitive information")
        return result