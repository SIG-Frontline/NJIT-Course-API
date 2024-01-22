import base64
import random
from enum import Enum
import requests
import urllib.parse
from utils import cond_cache_to_mongodb
import datetime

class Base64:
    @staticmethod
    def encode(data:str) -> str:
        utf8_encoded = data.encode('utf-8')
        base64_encoded = base64.b64encode(utf8_encoded)
        return base64_encoded.decode('utf-8')

    @staticmethod
    def decode(data:str) -> str:
        base64_decoded = base64.b64decode(data)
        utf8_decoded = base64_decoded.decode('utf-8')
        return utf8_decoded

def encode_params(params:dict[str, str]):
    new_params = {}
    for key, value in params.items():
        bkey = Base64.encode(str(random.randint(0, 99)))
        bval = Base64.encode(str(random.randint(0, 99)))
        new_params[bkey + Base64.encode(key)] = bval if value is None else bval + Base64.encode(value)
    return new_params

def decode_params(params:dict[str, str]):
    dec_params = {}
    if 'encoded' in params:
        dec_params['encoded'] = params['encoded']
        del params["encoded"]
    
    for key, value in params.items():
        tkey = Base64.decode(key[4:])
        if len(value) <= 4 or value[4:] == 'undefined':
            tval = None
        else:
            tval = Base64.decode(value[4:])
        dec_params[tkey] = tval
    return dec_params

class SemesterType(Enum):
    FALL = 90
    SPRING = 10
    WINTER = 95
    SUMMER = 50

SEMESTER_UPDATE_SCHEDULE = {
    1: [SemesterType.SPRING, SemesterType.WINTER],
    2: [SemesterType.SPRING],
    3: [SemesterType.SPRING, SemesterType.SUMMER],
    4: [SemesterType.SPRING, SemesterType.SUMMER, SemesterType.FALL],
    5: [SemesterType.SPRING, SemesterType.SUMMER, SemesterType.FALL],
    6: [SemesterType.FALL, SemesterType.SUMMER],
    7: [SemesterType.FALL, SemesterType.SUMMER],
    8: [SemesterType.FALL, SemesterType.SUMMER],
    9: [SemesterType.FALL, SemesterType.SUMMER],
    10: [SemesterType.FALL, SemesterType.WINTER],
    11: [SemesterType.FALL, SemesterType.SPRING, SemesterType.WINTER],
    12: [SemesterType.FALL, SemesterType.SPRING, SemesterType.WINTER]
}

class NJIT():
    @staticmethod
    def term_code(year:int, semester:SemesterType):
        return str(year) + str(semester.value)

    @staticmethod
    def refresh_term(term: str) -> bool:
        year = term[:-2]
        sem = SemesterType(int(term[-2:]))
        ...

    @staticmethod
    #@cond_cache_to_mongodb(db_name="NJIT_Course_API", collection_name="CS_Subjects")
    def get_subjects(term:str):
        params = {
            'attr':None,
            'offset':'0',
            'term':term,
            'max':'150',
        }
        params = encode_params(params)
        params['encoded'] = 'true'
        url_params = urllib.parse.urlencode(params)
        headers = {
            "content-type": "application/json;charset=utf-8"
        }
        response = requests.get("https://generalssb-prod.ec.njit.edu/BannerExtensibility/internalPb/virtualDomains.stuRegCrseSchedSubjList?" + url_params, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Request for NJIT Course Subjects Failed (Error {response.status_code})")
        
        return response.json()
    
    @staticmethod
    def get_sections(term:str, subject:str):
        params = {
            'attr':None,
            'subject':subject,
            'term':term,
            'prof_ucid':None
        }
        params = encode_params(params)
        params['encoded'] = 'true'
        url_params = urllib.parse.urlencode(params)
        headers = {
            "content-type": "application/json;charset=utf-8"
        }
        response = requests.get("https://generalssb-prod.ec.njit.edu/BannerExtensibility/internalPb/virtualDomains.stuRegCrseSchedSectionsExcel?" + url_params, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Request for NJIT Course Sections Failed (Error {response.status_code})")
        
        return response.json()
    
# term = NJIT.term_code(2024, SemesterType.FALL)
# subjects = NJIT.get_subjects(term)
# print(subjects)

# sections = NJIT.get_sections(term, "CS")
# print(sections)
if __name__ == "__main__":
    import time
    year = 2023
    while year > 2010:
        for sem in [SemesterType.SPRING, SemesterType.SUMMER, SemesterType.FALL, SemesterType.WINTER]:
            term = NJIT.term_code(year, sem)
            sections = NJIT.get_sections(term, "CS")
            
            profs = set()
            
            for sec in sections:
                if sec['COURSE'] == 'CS435':
                    profs.add(sec['INSTRUCTOR'])
            
            print(f"[{year}, {sem}]: {list(profs)}")
            time.sleep(2)
            
            
        year -= 1
            