import datetime
from sqlalchemy.schema import Column
from sqlalchemy import Uuid, String, DateTime, ForeignKey

from .baseDBModel import BaseModel
from .uuid import uuid

class EventUserModel(BaseModel):
    __tablename__ = "events_users"

    id = Column(Uuid, primary_key=True, comment="primary key", default=uuid)
    user_id = Column(Uuid, index=True, comment="link to user")
    event_id = Column(ForeignKey("events.id"), index=True, comment="link to event")