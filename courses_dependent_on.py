from interface.NJIT import NJIT
from interface.utils import mongo_client
from tabulate import tabulate

db = mongo_client["Schedule_Builder"]
course_collection = db["Course_Static"]

def reqs_contains(course, prereq):
    if len(course['courseInformation']['courses']) == 0:
        return False
    if 'prerequisites' not in course['courseInformation']['courses'][0]:
        return False
    prereqs = course['courseInformation']['courses'][0]['prerequisites']
    
    match_to = NJIT.format_course_code(prereq)
    for req in prereqs:
        if len(req['subjectCodePrerequisite']) > 0:
            req_str = f"{req['subjectCodePrerequisite']} {req['courseNumberPrerequisite']}"
        else:
            req_str = f"${req['tescCode']}"
        
        if req_str == match_to:
            return True
    return False

def reqs_to_str(course):
    if len(course['courseInformation']['courses']) == 0:
        return ""
    if 'prerequisites' not in course['courseInformation']['courses'][0]:
        return ""
    prereqs = course['courseInformation']['courses'][0]['prerequisites']
    req_str = ""
    for req in prereqs:
        req_str += req['connector'] + " "
        req_str += req['leftParenthesis'] + " "
        if len(req['subjectCodePrerequisite']) > 0:
            req_str += f" {req['subjectCodePrerequisite']} {req['courseNumberPrerequisite']} "
        else:
            req_str += f"${req['tescCode']}"
        req_str += req['rightParenthesis'] + " "
    req_str = " ".join(req_str.split())
    req_str = req_str.replace(" A ", " & ")
    req_str = req_str.replace(" O ", " | ")
    return req_str        

courses = list(course_collection.find({}))
courses = sorted(courses, key=lambda x: x['_id'])

header = ["Course Code", "Title", "Credits", "Requirements"]
table = []

for course in courses:
    e = reqs_contains(course, "CS 114") and not reqs_contains(course, "DS 340")
    if e:
        row = [course['_id'], "?", "?", "?"]
        title = course['courseInformation']['courses']
        if len(title) > 0:
            row[1] = f"{title[0].get('title', '?')}"
            row[2] = str(title[0].get('creditHourLow', '?'))
        row[3] = reqs_to_str(course)
        table.append(row)

print(tabulate(table, headers=header))