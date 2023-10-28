from sqlalchemy.schema import Column
from sqlalchemy import Uuid, String, DateTime

from .baseDBModel import BaseModel
from .uuid import uuid

class EventModel(BaseModel):
    __tablename__ = "events"

    id = Column(Uuid, primary_key=True, comment="primary key", default=uuid)
    name = Column(String, comment="name / label of the event")

    startdate = Column(DateTime, comment="when the event should start")
    enddate = Column(DateTime, comment="when the event should end")
