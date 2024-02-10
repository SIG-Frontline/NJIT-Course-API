from utils import mongo_client

db = mongo_client["NJIT_Course_API"]
course_collection = db["Courses"]

course = course_collection.find_one({'_id': 'BME 493'})
prereqs = course['courseInformation']['courses'][0]['prerequisites']

req_str = ""
for req in prereqs:
    req_str += req['connector'] + " "
    req_str += req['leftParenthesis'] + " "
    req_str += f" {req['subjectCodePrerequisite']} {req['courseNumberPrerequisite']} "
    req_str += req['rightParenthesis'] + " "
req_str = " ".join(req_str.split())
req_str = req_str.replace(" A ", " && ")
req_str = req_str.replace(" O ", " || ")
print(req_str)
print()

desc = " ".join(course['courseInformation']['courses'][0]['descriptionAdditional'])
print(desc)