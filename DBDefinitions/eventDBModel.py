from sqlalchemy.schema import Column
from sqlalchemy import Uuid, String

from .baseDBModel import BaseModel
from .uuid import uuid

class EventModel(BaseModel):
    __tablename__ = "events"

    id = Column(Uuid, primary_key=True, comment="primary key", default=uuid)
    name = Column(String)
