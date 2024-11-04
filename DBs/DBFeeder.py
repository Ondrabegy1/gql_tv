from functools import cache
from DBs.DBDefinitions import (
    ResultModel
)

from functools import cache


from sqlalchemy.future import select


def singleCall(asyncFunc):
    """Dekorator, ktery dovoli, aby dekorovana funkce byla volana (vycislena) jen jednou. Navratova hodnota je zapamatovana a pri dalsich volanich vracena.
    Dekorovana funkce je asynchronni.
    """
    resultCache = {}

    async def result():
        if resultCache.get("result", None) is None:
            resultCache["result"] = await asyncFunc()
        return resultCache["result"]

    return result

def get_demodata(asyncSessionMaker):
    pass

@cache

def determineResultTemplate():
    resultTemplates = [
        
    ]

    return resultTemplates

def determineDiscipline():
    disciplines = [
        
    ]

    return disciplines

@cache

def determineDisciplineSet():
    disciplineSets = [
        
    ]
    
    return disciplineSets