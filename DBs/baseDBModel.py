from sqlalchemy.orm import DeclarativeBase
import sqlalchemy
import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
import uuid

# Helper function to generate a new UUID as a string
def newUuidAsString():
    return f"{uuid.uuid1()}"

# Function to create a UUID column with optional name
def UUIDColumn(name=None):
    if name is None:
        return Column(String, primary_key=True, unique=True, default=newUuidAsString)
    else:
        return Column(
            name, String, primary_key=True, unique=True, default=newUuidAsString
        )

# Function to create a foreign key column with UUID type
def UUIDFKey(ForeignKey=None, nullable=False, **kwargs):
    if ForeignKey is None:
        return Column(
            String, index=True, nullable=nullable, **kwargs
        )
    else:
        return Column(
            ForeignKey, index=True, nullable=nullable, **kwargs
        )


# Base model for all database models
class BaseModel(DeclarativeBase):

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="tvorba záznamu")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), onupdate=sqlalchemy.sql.func.now(), comment="poslední změna")
    changedby_id = UUIDFKey(nullable=True, comment = "změnil/a")
    createdby_id = UUIDFKey(nullable=True, comment = "vytvořil/a")
    rbacobject_id = UUIDFKey(nullable=True, comment = "RBAC objekt")
