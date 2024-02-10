import requests
from course_schedule import NJIT, SemesterType
from prereq_parser import get_course_desc, get_course_reqs, split_course_code
from utils import mongo_client
import time
import datetime
import json


session = requests.Session()

# Set initial cookies from DegreeWorks
initial_cookies = ...
session.cookies.update(initial_cookies)


courses = set()
    
year = 2024
while year > 2010:
    for sem in [SemesterType.SPRING, SemesterType.SUMMER, SemesterType.FALL, SemesterType.WINTER]:
        term = NJIT.term_code(year, sem)
        subjects = NJIT.get_subjects(term)
        
        db = mongo_client["NJIT_Course_API"]
        collection = db["Courses"]
        
        for s in subjects:
            subject = s['SUBJECT']
            sections = NJIT.get_sections(term, subject)
            print(f"[{term}]: {subject} ({len(courses)})")
            for sec in sections:
                course: str = sec['COURSE']
                if course in courses:
                    continue
                else:      
                    c1 = course.replace(' ', '')
                    c2 = split_course_code(c1)
                    
                    cname = " ".join(c2)
                    
                    if collection.find_one({'_id':cname}) != None:
                        print("Found " + cname)
                        courses.add(course)
                        continue
                    
                    print("Getting " + cname)
                    response = session.get(f'https://dw-prod.ec.njit.edu/responsiveDashboard/api/course-link?discipline={c2[0]}&number={c2[1]}&=')
                    time.sleep(0.25)
                    obj = response.json()
                    #print(session.cookies.get_dict())

                    obj['_id'] = cname
                    obj['updated'] = datetime.date.today().strftime("%d/%m/%Y")
                    
                    collection.insert_one(obj)
                    courses.add(course)
            time.sleep(0.5)
    year -= 1

print(courses)


#Print cookies for re-use
print(session.cookies.get_dict())

