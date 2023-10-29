from functools import cache
from DBDefinitions import (
    EventModel
    )
from sqlalchemy.future import select


import os
import json
from uoishelpers.feeders import ImportModels
import datetime
import uuid

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
            if "id" in key:
                json_dict[key] = uuid.UUID(value)
        return json_dict


    with open("./systemdata.json", "r", encoding='utf-8') as f:
        jsonData = json.load(f, object_hook=datetime_parser)

    return jsonData

async def initDB(asyncSessionMaker):

    defaultNoDemo = "False"
    default = "True"
    if default == os.environ.get("DEMO", defaultNoDemo):
        dbModels = []
    else:
        dbModels = [
            EventModel
        ]

    jsonData = get_demodata()
    await ImportModels(asyncSessionMaker, dbModels, jsonData)
    pass