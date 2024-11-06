from sqlalchemy.future import select
import strawberry

from DBs.baseDBModel import BaseModel
from DBs.DBDefinitions import GroupTypeModel, RoleTypeModel


def AsyncSessionFromInfo(info):
    # Retrieves the asynchronous session from the GraphQL context
    return info.context["session"]


def UserFromInfo(info):
    # Retrieves the user from the GraphQL context
    return info.context["user"]


class BasePermission(strawberry.permission.BasePermission):
    message = "User is not authenticated"

    async def has_permission(
        self, source, info: strawberry.types.Info, **kwargs
    ) -> bool:
        # Default permission check, this is the base permission class
        print("BasePermission", source)
        print("BasePermission", self)
        print("BasePermission", kwargs)
        return True


class GroupEditorPermission(BasePermission):
    message = "User is not authenticated"

    async def canEditGroup(session, group_id, user_id):
        # Check if the user has the role to edit a group
        stmt = select(RoleModel).filter_by(group_id=group_id, user_id=user_id)
        dbRecords = await session.execute(stmt).scalars()
        dbRecords = [*dbRecords]  # Convert to list
        if len(dbRecords) > 0:
            return True
        else:
            return False

    async def has_permission(
        self, source, info: strawberry.types.Info, **kwargs
    ) -> bool:
        # Check if the user has permission to edit the group
        print("GroupEditorPermission", source)
        print("GroupEditorPermission", self)
        print("GroupEditorPermission", kwargs)
        # _ = await self.canEditGroup(session,  source.id, ...)
        print("GroupEditorPermission")
        return True


class UserEditorPermission(BasePermission):
    message = "User is not authenticated"

    async def has_permission(
        self, source, info: strawberry.types.Info, **kwargs
    ) -> bool:
        # Check if the user has permission to edit user data
        print("UserEditorPermission", source)
        print("UserEditorPermission", self)
        print("UserEditorPermission", kwargs)
        return True


class UserGDPRPermission(BasePermission):
    message = "User is not authenticated"

    async def has_permission(
        self, source, info: strawberry.types.Info, **kwargs
    ) -> bool:
        # Check if the user has permission for GDPR-related actions
        print("UserGDPRPermission", source)
        print("UserGDPRPermission", self)
        print("UserGDPRPermission", kwargs)
        return True