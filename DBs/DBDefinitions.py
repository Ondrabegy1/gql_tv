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
from .baseDBModel import BaseModel
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

# Discipline model
class DisciplineModel(BaseModel):
    __tablename__ = "tv_discipline"
   
    id = UUIDColumn()
    name = Column(String, comment="název disciplíny")
    nameEn = Column(String, nullable=True, comment="název disciplíny v ENG")
    description = Column(String, nullable=True, comment="popis disciplíny")

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="tvorba záznamu")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), onupdate=sqlalchemy.sql.func.now(), comment="poslední změna")
    changedby_id = UUIDFKey(nullable=True, comment = "změnil/a")
    createdby_id = UUIDFKey(nullable=True, comment = "vytvořil/a")
    rbacobject_id = UUIDFKey(nullable=True, comment = "RBAC objekt")

    resultTemplates = relationship("ResultTemplateModel", back_populates="discipline")

# Discipline set model
class DisciplineSetModel(BaseModel):
    __tablename__ = "tv_discipline_set"
   
    id = UUIDColumn()
    name = Column(String, comment="název souboru disciplín")
    nameEn = Column(String, nullable=True, comment="název souboru disciplín v ENG")
    description = Column(String, nullable=True, comment="popis souboru disciplín")
    minimumPoints = Column(Integer, nullable=True, comment="minimální počet bodů")

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="tvorba záznamu")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), onupdate=sqlalchemy.sql.func.now(), comment="poslední změna")
    changedby_id = UUIDFKey(nullable=True, comment = "změnil/a")
    createdby_id = UUIDFKey(nullable=True, comment = "vytvořil/a")
    rbacobject_id = UUIDFKey(nullable=True, comment = "RBAC objekt")

    resultTemplates = relationship("ResultTemplateModel", back_populates="disciplineSet")
    norms = relationship("NormModel", back_populates="disciplineSet")

# Result template model
class ResultTemplateModel(BaseModel):
    __tablename__ = "tv_result_template"
   
    id = UUIDColumn()
    discipline_id = UUIDFKey(ForeignKey("tv_discipline.id"), comment="id disciplíny")
    discipline_set_id = UUIDFKey(ForeignKey("tv_discipline_set.id"), comment="id souboru disciplín")
    effective_date = Column(DateTime, comment="datum účinnosti")
    expiry_date = Column(DateTime, nullable=True, comment="datum zániku")
    point_range = Column(String, comment="rozsah bodů")
    point_type = Column(String, comment="typ bodů")

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="tvorba záznamu")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), onupdate=sqlalchemy.sql.func.now(), comment="poslední změna")
    changedby_id = UUIDFKey(nullable=True, comment = "změnil/a")
    createdby_id = UUIDFKey(nullable=True, comment = "vytvořil/a")
    rbacobject_id = UUIDFKey(nullable=True, comment = "RBAC objekt")

    discipline = relationship("DisciplineModel", back_populates="resultTemplates")
    disciplineSet = relationship("DisciplineSetModel", back_populates="resultTemplates")

# Result model
class ResultModel(BaseModel):
    __tablename__ = "tv_result"

    id = UUIDColumn()
    tested_person_id = UUIDFKey(comment="id testované osoby")
    examiner_person_id = UUIDFKey(comment="id zkoušející osoby")
    datetime = Column(DateTime, comment="datum a čas výsledku")
    result = Column(String, comment="výsledek")
    note = Column(String, nullable=True, comment="poznámka")

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="tvorba záznamu")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), onupdate=sqlalchemy.sql.func.now(), comment="poslední změna")
    changedby_id = UUIDFKey(nullable=True, comment = "změnil/a")
    createdby_id = UUIDFKey(nullable=True, comment = "vytvořil/a")
    rbacobject_id = UUIDFKey(nullable=True, comment = "RBAC objekt")

# Norm model
class NormModel(BaseModel):
    __tablename__ = "tv_norm"

    id = UUIDColumn()
    discipline_set_id = UUIDFKey(ForeignKey("tv_discipline_set.id"), comment="id souboru disciplín")
    effective_date = Column(DateTime, comment="datum účinnosti")
    expiry_date = Column(DateTime, nullable=True, comment="datum zániku")
    male = Column(Boolean, default=False, comment="muž")
    female = Column(Boolean, default=False, comment="žena")
    age_minimal = Column(Integer, comment="minimální věk")
    age_maximal = Column(Integer, comment="maximální věk")
    result_minimal_value = Column(Integer, comment="minimální hodnota výsledku")
    result_maximal_value = Column(Integer, comment="maximální hodnota výsledku")
    points = Column(Integer, comment="body")

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="tvorba záznamu")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), onupdate=sqlalchemy.sql.func.now(), comment="poslední změna")
    changedby_id = UUIDFKey(nullable=True, comment = "změnil/a")
    createdby_id = UUIDFKey(nullable=True, comment = "vytvořil/a")
    rbacobject_id = UUIDFKey(nullable=True, comment = "RBAC objekt")

    disciplineSet = relationship("DisciplineSetModel", back_populates="norms")

    @validates('male', 'female')
    def validate_gender(self, key, value):
        if key == 'male' and value:
            assert not self.female, "nemůže být zároveň muž a žena"
        if key == 'female' and value:
            assert not self.male, "nemůže být zároveň muž a žena"
        return value