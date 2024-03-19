import requests
import time
import datetime
import json

from NJIT import NJIT, SemesterType
from utils import mongo_client

dw_majors = ['APPH', 'ARCH', 'BIOC', 'BNFO', 'BIOL', 'BMED', 'BINF', 'BIOP', 'BIS', 'BUS', 'CHE', 'CHM', 'CE', 'COMM', 'CSCI', 'COE', 'CS', 'CBUS', 'CIM', 'CPSY', 'DSCO', 'DSSO', 'EE', 'ESC', 'EVSC', 'FTEC', 'FRSC', 'GEN', 'HCI', 'ID', 'IE', 'IS', 'IT', 'MFEN', 'MTEN', 'MATH', 'ME', 'STS', 'UDCC', 'UDEN', 'UDSL', 'WIS']


session = requests.Session()

# Set initial cookies from DegreeWorks
initial_cookies =  {}
id_8digit = ...
session.cookies.update(initial_cookies)

def get_course_info(discipline, number):
    global session
    response = session.get(f'https://dw-prod.ec.njit.edu/responsiveDashboard/api/course-link?discipline={discipline}&number={number}&=')
    return response.json()

def get_major(major, catalogYear):
    if major not in dw_majors:
        raise ValueError("Invalid Major")
    headers = {
        "studentId":str(id_8digit),
        "isIncludeInprogress":False,
        "isIncludePreregistered":False,
        "isKeepCurriculum":False,
        "school":"U",
        "degree":"BS",
        "catalogYear":catalogYear,
        "goals":[{"code":"MAJOR","value":str(major),"catalogYear":str(catalogYear)}],
        "classes":[]
    }
    url = "https://dw-prod.ec.njit.edu/responsiveDashboard/api/audit"
    response = session.get(url, headers=headers)
    
    robj = response.json()
    relevant_blocks = [x for x in robj['blockArray'] if x['requirementType'] in ['OTHER', 'MAJOR', 'MINOR']]
    return relevant_blocks

if __name__ == "__main__":
    sec_collection = mongo_client['Schedule_Builder']['Sections']
    result = sec_collection.aggregate([
        {
            '$group': {
                '_id': '$COURSE', 
                'amt': {
                    '$count': {}
                }
            }
        }
    ])
    
    collection = mongo_client['Schedule_Builder']['Course_Static']
        
    for sec in result:
        course: str = sec['_id']     
        c1 = course.replace(' ', '')
        c2 = NJIT.split_course_code(c1)
        
        cname = " ".join(c2)
        
        if collection.find_one({'_id':cname}) != None:
            print("Found " + cname)
            continue
        
        print("Getting " + cname)
        response = session.get(f'https://dw-prod.ec.njit.edu/responsiveDashboard/api/course-link?discipline={c2[0]}&number={c2[1]}&=')
        time.sleep(0.25)
        obj = response.json()
        #print(session.cookies.get_dict())

        obj['_id'] = cname
        obj['updated'] = datetime.date.today().strftime("%d/%m/%Y")
        
        collection.insert_one(obj)


    #Print cookies for re-use
    print(session.cookies.get_dict())

