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

# Decorator to cache the result of a single async function call
def singleCall(asyncFunc):
    resultCache = {}

    async def result():
        if resultCache.get("result", None) is None:
            resultCache["result"] = await asyncFunc()
        return resultCache["result"]

    return result

# Async function to fill the disciplines table with predefined data
@singleCall
async def fill_disciplines(asyncSessionMaker):
    async with asyncSessionMaker() as session:
        async with session.begin():
            disciplines = [
                {
                    "name": "Běh 4 x 10 m (s)", "nameEn": "DODĚLAT", "description": "Člunkový běh 4 x 10 metrů"
                },
                {
                    "name": "Běh 10 x 10 m (s)", "nameEn": "DODĚLAT", "description": "Člunkový běh 10 x 10 metrů"
                },
                # Add more disciplines here
            ]
            for discipline in disciplines:
                session.add(DisciplineModel(**discipline))

# Async function to fill the discipline sets table with predefined data
@singleCall
async def fill_discipline_sets(asyncSessionMaker):
    async with asyncSessionMaker() as session:
        async with session.begin():
            discipline_sets = [
                {
                    "name": "1. ročník ZS", "nameEn": "1. year ZS", "description": "Disciplíny pro zimní semestr 1. ročníku", "minimumPoints": 9
                },
                # Add more discipline sets here
            ]
            for discipline_set in discipline_sets:
                session.add(DisciplineSetModel(**discipline_set))

# Async function to fill the result templates table with predefined data
@singleCall
async def fill_result_templates(asyncSessionMaker):
    async with asyncSessionMaker() as session:
        async with session.begin():
            # Get discipline and discipline set IDs for the result templates
            discipline_id = await session.scalar(select(DisciplineModel.id).limit(1))
            discipline_set_id = await session.scalar(select(DisciplineSetModel.id).limit(1))
            result_templates = [
                {
                    "discipline_id": discipline_id, 
                    "discipline_set_id": discipline_set_id, 
                    "effective_date": datetime.datetime.now(), 
                    "point_range": "0-48", 
                    "point_type": "integer"
                },
                # Add more result templates here
            ]
            for result_template in result_templates:
                session.add(ResultTemplateModel(**result_template))

# Async function to fill the results table with predefined data
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
                    "result": "9", 
                    "note": "Vyhovující"
                },
                # Add more results here
            ]
            for result in results:
                session.add(ResultModel(**result))

# Async function to fill the norms table with predefined data
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
                    "age_maximal": 25, 
                    "result_minimal_value": 9, 
                    "result_maximal_value": 48, 
                    "points": 10
                },
                # Add more norms here
            ]
            for norm in norms:
                session.add(NormModel(**norm))

# Function to load demo data from a JSON file
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

    # Load data from 'systemdata.json' and parse datetime fields
    with open("./systemdata.json", "r") as f:
        jsonData = json.load(f, object_hook=datetime_parser)

    return jsonData

# Async function to initialize the database with demo data or predefined models
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
