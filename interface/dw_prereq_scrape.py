import requests
import time
import datetime
import json

from NJIT import NJIT, SemesterType
from utils import mongo_client

dw_majors = ['APPH', 'ARCH', 'BIOC', 'BNFO', 'BIOL', 'BMED', 'BINF', 'BIOP', 'BIS', 'BUS', 'CHE', 'CHM', 'CE', 'COMM', 'CSCI', 'COE', 'CS', 'CBUS', 'CIM', 'CPSY', 'DSCO', 'DSSO', 'EE', 'ESC', 'EVSC', 'FTEC', 'FRSC', 'GEN', 'HCI', 'ID', 'IE', 'IS', 'IT', 'MFEN', 'MTEN', 'MATH', 'ME', 'STS', 'UDCC', 'UDEN', 'UDSL', 'WIS']


session = requests.Session()

# Set initial cookies from DegreeWorks
initial_cookies = {
		"AMCV_4D6368F454EC41940A4C98A6@AdobeOrg": "1075005958|MCIDTS|19710|MCMID|16718154813653225160268188034875386277|MCAID|NONE|MCOPTOUT-1702920169s|NONE|vVersion|4.4.1",
		"amplitude_id_9f6c0bb8b82021496164c672a7dc98d6_edmnjit.edu": "eyJkZXZpY2VJZCI6ImI0MzYxZDY1LTE1MTAtNDdlOS04ZmM5LWM3NmIwZjJkMmY3NFIiLCJ1c2VySWQiOm51bGwsIm9wdE91dCI6ZmFsc2UsInNlc3Npb25JZCI6MTcwMjY3MzUxMDU4MiwibGFzdEV2ZW50VGltZSI6MTcwMjY3MzY2NTcxNiwiZXZlbnRJZCI6MCwiaWRlbnRpZnlJZCI6Niwic2VxdWVuY2VOdW1iZXIiOjZ9",
		"NAME": " Kamil Muhammad Arif",
		"ph_foZTeM1AW8dh5WkaofxTYiInBhS4XzTzRqLs50kVziw_posthog": "{\"distinct_id\":\"188f35b1035164a-01b13ea5bd92088-d515429-1fa400-188f35b10362756\",\"$device_id\":\"188f35b1035164a-01b13ea5bd92088-d515429-1fa400-188f35b10362756\",\"$user_state\":\"anonymous\",\"extension_version\":\"1.5.5\",\"$sesid\":[1687747298886,\"188f586287e158b-00d67f74aac6cf8-d515429-1fa400-188f586287f14fc\",1687746390142],\"$session_recording_enabled_server_side\":false,\"$autocapture_disabled_server_side\":false,\"$active_feature_flags\":[],\"$enabled_feature_flags\":{\"enable-session-recording\":false,\"sourcing\":false,\"only-company-edit\":false,\"job-lists\":false},\"$feature_flag_payloads\":{}}",
		"REFRESH_TOKEN": "Bearer+eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIzMTUxMDU5MyIsInVzZXJDbGFzcyI6IlNUVSIsImNvbW1vblRva2VuSWQiOiIiLCJhcHBOYW1lIjoiZGVncmVld29ya3MiLCJpc3MiOiJFbGx1Y2lhbiBEZWdyZWUgV29ya3MiLCJzZXNzaW9uSWQiOiJiYWUxMDNlOC0yMGY4LTRkMDItYjVkMy03YWY4NzZlMWE2NDEiLCJleHBpcmVJbmNyZW1lbnRTZWNvbmRzIjo1OTk5NDAsImFsdElkIjoia21hNTYiLCJpbnRlcm5hbElkIjoiMzE1MTA1OTMiLCJuYW1lIjoiQXJpZiwgS2FtaWwgTXVoYW1tYWQiLCJleHAiOjE3MDkwNjUzMTUsImlhdCI6MTcwODQ2NTM3NSwianRpIjoiODhmMTdmZGUtNGFmNi00ZWM3LTg4ODUtNTZhODU3ZWM3Nzg1In0.4ln8K_WwjOOK7IUqvBCpxpP8bGZNobrJRCispm1qV3s",
		"X-AUTH-TOKEN": "Bearer+eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIzMTUxMDU5MyIsInVzZXJDbGFzcyI6IlNUVSIsImFwcE5hbWUiOiJkZWdyZWV3b3JrcyIsInJvbGVzIjpbIlNEQVVESVQiLCJTREFVRFBERiIsIlNEQVVEUkVWIiwiU0RHUEFBRFYiLCJTREdQQUdSRCIsIlNER1BBVFJNIiwiU0RISVNUIiwiU0RMT0tBSEQiLCJTRFBFVFZFVyIsIlNEU1RVTUUiLCJTRFdFQjMxIiwiU0RXRUIzMyIsIlNEV0VCMzYiLCJTRFdIQVRJRiIsIlNEV09SS1MiLCJTRFhNTDMxIiwiU0VQUEFERCIsIlNFUFBBVUQiLCJTRVBQREVMTCIsIlNFUFBMQU4iLCJTRVBQTkFERCIsIlNFUFBOREVMIiwiU0VQUFNFTCIsIlNFUFBURU1QIiwiU0VQUFdJRiJdLCJpc3MiOiJFbGx1Y2lhbiBEZWdyZWUgV29ya3MiLCJzZXNzaW9uSWQiOiJiYWUxMDNlOC0yMGY4LTRkMDItYjVkMy03YWY4NzZlMWE2NDEiLCJhbHRJZCI6ImttYTU2IiwiaW50ZXJuYWxJZCI6IjMxNTEwNTkzIiwibmFtZSI6IkFyaWYsIEthbWlsIE11aGFtbWFkIiwiZXhwIjoxNzA5MDY1OTM4LCJpYXQiOjE3MDg0NjU5OTgsImp0aSI6IjMzNWQ3Yzk0LTlkZGEtNDM3MS05NTEzLWQ1ZmE5MzI1Y2JkYyJ9._wSZXuUdoEKRjK4JwcFQvWtAxnPpCrsKaFvGsn42hcQ"
	}
id_8digit = 31510593
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

