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
from sqlalchemy.ext.declarative import declarative_base
import uuid

BaseModel = declarative_base()

def newUuidAsString():
    return f"{uuid.uuid1()}"

def UUIDColumn(name=None):
    if name is None:
        return Column(String, primary_key=True, unique=True, default=newUuidAsString)
    else:
        return Column(
            name, String, primary_key=True, unique=True, default=newUuidAsString
        )

def UUIDFKey(ForeignKey=None, nullable=False):
    if ForeignKey is None:
        return Column(
            String, index=True, nullable=nullable
        )
    else:
        return Column(
            ForeignKey, index=True, nullable=nullable
        )

class DisciplineModel(BaseModel):
    __tablename__ = "tv_discipline"
   
    id = UUIDColumn()
    name = Column(String, comment="název disciplíny")
    nameEn = Column(String, nullable=True, comment="název disciplíny v ENG")
    description = Column(String, nullable=True, comment="popis disciplíny")

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="tvorba záznamu")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), onupdate=sqlalchemy.sql.func.now(), comment="poslední změna")
    changedby = UUIDFKey(nullable=True)

    resultTemplates = relationship("ResultTemplateModel", back_populates="discipline", comment="šablony výsledků")

class DisciplineSetModel(BaseModel):
    __tablename__ = "tv_discipline_set"
   
    id = UUIDColumn()
    name = Column(String, comment="název souboru disciplín")
    nameEn = Column(String, nullable=True, comment="název souboru disciplín v ENG")
    description = Column(String, nullable=True, comment="popis souboru disciplín")
    minimumPoints = Column(Integer, nullable=True, comment="minimální počet bodů")

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="tvorba záznamu")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), onupdate=sqlalchemy.sql.func.now(), comment="poslední změna")
    changedby = UUIDFKey(nullable=True)

    resultTemplates = relationship("ResultTemplateModel", back_populates="disciplineSet", comment="šablony výsledků")
    norms = relationship("NormModel", back_populates="disciplineSet", comment="normy")

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
    changedby = UUIDFKey(nullable=True)

    discipline = relationship("DisciplineModel", back_populates="resultTemplates", comment="disciplína")
    disciplineSet = relationship("DisciplineSetModel", back_populates="resultTemplates", comment="soubor disciplín")

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
    changedby = UUIDFKey(nullable=True)

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
    changedby = UUIDFKey(nullable=True)

    disciplineSet = relationship("DisciplineSetModel", back_populates="norms", comment="soubor disciplín")

    @validates('male', 'female')
    def validate_gender(self, key, value):
        if key == 'male' and value:
            assert not self.female, "nemůže být zároveň muž a žena"
        if key == 'female' and value:
            assert not self.male, "nemůže být zároveň muž a žena"
        return value