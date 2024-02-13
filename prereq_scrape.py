from course_schedule import NJIT, SemesterType
from prereq_parser import get_course_desc, get_course_reqs, format_course_code
from utils import mongo_client
import time
import json


if __name__ == "__main__":    
    courses = set()
        
    year = 2024
    while year > 2010:
        for sem in [SemesterType.SPRING, SemesterType.SUMMER, SemesterType.FALL, SemesterType.WINTER]:
            term = NJIT.term_code(year, sem)
            subjects = NJIT.get_subjects(term)
            for s in subjects:
                subject = s['SUBJECT']
                sections = NJIT.get_sections(term, subject)
                print(f"[{term}]: {subject} ({len(courses)})")
                for sec in sections:
                    course: str = sec['COURSE']
                    if course in courses:
                        continue
                    else:                        
                        db = mongo_client["NJIT_Course_API"]
                        collection = db["LLM_Cache"]
                        c1 = course.replace(' ', '')
                        c2 = format_course_code(c1)
                        item = collection.find_one({'$or': [{'name':c1}, {'name':c2}]})
                        if item is not None:
                            continue
                        
                        desc = get_course_desc(course)
                        print(desc)
                        reqs = get_course_reqs(course_code=course, desc=desc)
                        print(json.dumps(reqs, indent=2)) 
                                           
                        courses.add(course)
                        input()
                    
                
                time.sleep(0.25)
            
            
        year -= 1

    print(courses)