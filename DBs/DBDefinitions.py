#FK = foreign key z jiné databáze

import sqlalchemy
import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Integer,
    DateTime,
    ForeignKey,
    Sequence,
    Table,
    Boolean,
    Uuid
)
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship
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

def UUIDFKey(*, ForeignKey=None, nullable=False):
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
    nameEn = Column(String, comment="název disciplíny v ENG")
    description = Column(String, comment="popis disciplíny")

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="tvorba záznamu")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="posledni změna")
    changedby = UUIDFKey(nullable=True)

    resultTemplate = relationship("ResultTemplateModel", back_populates="discipline", comment="šablony výsledků")

class DisciplineSetModel(BaseModel):
    __tablename__ = "tv_discipline.set"
   
    id = UUIDColumn()
    name = Column(String, comment="název souboru disciplín")
    nameEn = Column(String, comment="název souboru disciplín v ENG")
    description = Column(String, comment="popis souboru disciplín")
    minimumPoints = Column(String, comment="minimální počet bodů")

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="tvorba záznamu")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="poslední změna")
    changedby = UUIDFKey(nullable=True)

    resultTemplates = relationship("ResultTemplateModel", back_populates="disciplineSet", comment="šablony výsledků")

class ResultTemplateModel(BaseModel):
    __tablename__ = "tv_result.template"
   
    id = UUIDColumn()
    discipline_id = UUIDFKey(nullable=True, comment="id disciplíny")
    discipline_set_id = UUIDFKey(nullable=True, comment="id souboru disciplín")
    effective_date = Column(DateTime, comment="datum účinnosti")
    expiry_date = Column(DateTime, comment="datum zániku")
    point_range = Column(String, comment="rozsah bodů")
    point_type = Column(String, comment="typ bodů")

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="tvorba záznamu")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="poslední změna")
    changedby = UUIDFKey(nullable=True)

    discipline = relationship("DisciplineModel", back_populates="resultTemplate", comment="disciplína")
    disciplineSet = relationship("DisciplineSetModel", back_populates="resultTemplates", comment="soubor disciplín")

class ResultModel(BaseModel):
    __tablename__ = "tv_result"

    id = UUIDColumn()
    tested_person_id = UUIDFKey(nullable=True, comment="id testované osoby")
    examiner_person_id = UUIDFKey(nullable=True, comment="id zkoušející osoby")
    #DSRelation_id = (nemám tušení co to je)
    datetime = Column(DateTime, comment="datum a čas výsledku")
    result = Column(String, comment="výsledek")
    note = Column(String, comment="poznámka")

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="tvorba záznamu")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="poslední změna")
    changedby = UUIDFKey(nullable=True)

class NormModle(BaseModel):
    __tablename__ = "tv_norm"

    id = UUIDColumn()
    #DSRelation_id = (nemám tušení co to je)
    effective_date = Column(DateTime, comment="datum účinnosti")
    expiry_date = Column(DateTime, comment="datum zániku")
    gender = Column(String, comment="pohlaví")
    age_minimal = Column(Integer, comment="minimální věk")
    age_maximal = Column(Integer, comment="maximální věk")
    result_minimal_value = Column(Integer, comment="minimální hodnota výsledku")
    result_maximal_value = Column(Integer, comment="maximální hodnota výsledku")
    points = Column(Integer, comment="body")

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="tvorba záznamu")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="poslední změna")
    changedby = UUIDFKey(nullable=True)