import datetime
import os
import json
import asyncio
from functools import cache
from uoishelpers.feeders import ImportModels
from sqlalchemy.future import select
from DBs.DBDefinitions import (
    DisciplineModel,
    DisciplineSetModel,
    ResultTemplateModel,
    ResultModel,
    NormModel
)

def singleCall(asyncFunc):

    resultCache = {}

    async def result():
        if resultCache.get("result", None) is None:
            resultCache["result"] = await asyncFunc()
        return resultCache["result"]

    return result

@singleCall
async def fill_disciplines(asyncSessionMaker):
    async with asyncSessionMaker() as session:
        async with session.begin():
            disciplines = [
                {"name": "Biology", "nameEn": "Biology", "description": "Study of living organisms"},
                {"name": "Chemistry", "nameEn": "Chemistry", "description": "Study of substances and their properties"},
                # Add more disciplines here...
            ]
            for discipline in disciplines:
                session.add(DisciplineModel(**discipline))

@singleCall
async def fill_discipline_sets(asyncSessionMaker):
    async with asyncSessionMaker() as session:
        async with session.begin():
            discipline_sets = [
                {"name": "Science", "nameEn": "Science Set", "description": "Set of science disciplines", "minimumPoints": 50},
                # Add more discipline sets here...
            ]
            for discipline_set in discipline_sets:
                session.add(DisciplineSetModel(**discipline_set))

@singleCall
async def fill_result_templates(asyncSessionMaker):
    async with asyncSessionMaker() as session:
        async with session.begin():
            discipline_id = await session.scalar(select(DisciplineModel.id).limit(1))
            discipline_set_id = await session.scalar(select(DisciplineSetModel.id).limit(1))
            result_templates = [
                {
                    "discipline_id": discipline_id, 
                    "discipline_set_id": discipline_set_id, 
                    "effective_date": datetime.datetime.now(), 
                    "point_range": "0-100", 
                    "point_type": "integer"
                },
                # Add more result templates here...
            ]
            for result_template in result_templates:
                session.add(ResultTemplateModel(**result_template))

@singleCall
async def fill_results(asyncSessionMaker):
    async with asyncSessionMaker() as session:
        async with session.begin():
            result_template_id = await session.scalar(select(ResultTemplateModel.id).limit(1))
            results = [
                {
                    "tested_person_id": "1", 
                    "examiner_person_id": "2", 
                    "datetime": datetime.datetime.now(), 
                    "result": "85", 
                    "note": "Good performance"
                },
                # Add more results here...
            ]
            for result in results:
                session.add(ResultModel(**result))

@singleCall
async def fill_norms(asyncSessionMaker):
    async with asyncSessionMaker() as session:
        async with session.begin():
            discipline_set_id = await session.scalar(select(DisciplineSetModel.id).limit(1))
            norms = [
                {
                    "discipline_set_id": discipline_set_id, 
                    "effective_date": datetime.datetime.now(), 
                    "gender": "male", 
                    "age_minimal": 18, 
                    "age_maximal": 30, 
                    "result_minimal_value": 50, 
                    "result_maximal_value": 100, 
                    "points": 10
                },
                # Add more norms here...
            ]
            for norm in norms:
                session.add(NormModel(**norm))

def get_demodata():
    def datetime_parser(json_dict):
        for (key, value) in json_dict.items():
            if key in ["startdate", "enddate", "lastchange", "created"]:
                if value is None:
                    dateValueWOtzinfo = None
                else:
                    try:
                        dateValue = datetime.datetime.fromisoformat(value)
                        dateValueWOtzinfo = dateValue.replace(tzinfo=None)
                    except:
                        print("jsonconvert Error", key, value, flush=True)
                        dateValueWOtzinfo = None
                json_dict[key] = dateValueWOtzinfo
        return json_dict

    with open("./systemdata.json", "r") as f:
        jsonData = json.load(f, object_hook=datetime_parser)

    return jsonData

async def initDB(asyncSessionMaker):

    defaultNoDemo = "False"
    if defaultNoDemo == os.environ.get("DEMO", defaultNoDemo):
        dbModels = [
            DisciplineModel,
            DisciplineSetModel,
            ResultTemplateModel,
            ResultModel,
            NormModel
        ]
    else:
        dbModels = [
            DisciplineModel,
            DisciplineSetModel,
            ResultTemplateModel,
            ResultModel,
            NormModel
        ]

    jsonData = get_demodata()
    await ImportModels(asyncSessionMaker, dbModels, jsonData)
    pass