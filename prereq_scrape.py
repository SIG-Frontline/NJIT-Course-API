from course_schedule import NJIT, SemesterType
from prereq_parser import get_course_desc, get_course_reqs, format_course_code
from utils import mongo_client
import time
import json

def print_side_by_side(text, json_val: dict):
    # Convert JSON string to a pretty-printed version
    json_pretty = json.dumps(json_val, indent=2)

    # Split both text and JSON into lines
    text_lines = text.split('\n')
    json_lines = json_pretty.split('\n')

    # Calculate the maximum width of the text lines
    max_text_width = max(len(line) for line in text_lines)

    # Iterate over the maximum number of lines between text and JSON
    for i in range(max(len(text_lines), len(json_lines))):
        # Get the current line from text and JSON, or empty string if none
        text_line = text_lines[i] if i < len(text_lines) else ''
        json_line = json_lines[i] if i < len(json_lines) else ''

        # Print the lines side by side, separated by a tab or some spaces
        print(f"{text_line.ljust(max_text_width)}    {json_line}")


if __name__ == "__main__":
    # Code that looks at all professors that have taught a specific course over time
    # Not relevant to the rest of the file, should be deleted at some point
    
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