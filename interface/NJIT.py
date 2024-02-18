import base64
import random
from enum import Enum
import requests
import urllib.parse
from bs4 import BeautifulSoup
import time
import xml.etree.ElementTree as ET
import re
from functools import lru_cache

from .utils import cond_cache_to_mongodb

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

def _xml_to_raw_text(xml_string) -> str:
    try:
        # Parse the XML string
        root = ET.fromstring(xml_string)

        # Function to recursively extract text from each element
        def recurse_extract_text(element):
            text = element.text or ""
            xml_text = None
            try:
                xml_text = ET.fromstring(text)
            except:
                pass
            finally:
                if xml_text != None:
                    text = recurse_extract_text(xml_text)
            for child in element:
                text += recurse_extract_text(child)
            text += element.tail or ""
            return text

        # Extract text starting from the root
        raw_text = recurse_extract_text(root)

        return raw_text.strip()
    except ET.ParseError as e:
        return f"Error parsing XML: {e}"

class SemesterType(Enum):
    FALL = 90
    SPRING = 10
    WINTER = 95
    SUMMER = 50

class NJIT():
    @staticmethod
    def term_code(year:int, semester:SemesterType):
        """Generates a term code that is compatible with the Course Schedule's internal API

        Args:
            year (int): The (calendar) year of the term
            semester (SemesterType): The semester within the calendar year being defined

        Returns:
            _type_: str
        """
        return str(year) + str(semester.value)

    _cterm: tuple[str | None, int] = (None, -1)
    
    @staticmethod
    @lru_cache(maxsize=1)
    def current_term() -> str | None:
        """Returns the term code of the current ongoing term

        Raises:
            Exception: If the request fails (unlikely except in the case of server failure or ratelimit)

        Returns:
            str | None: The term code, or None if nothing was found
        """
        prev_result, prev_time = NJIT._cterm
        if time.time() - prev_time < 86400:
            return prev_result
        
        url = 'https://www.njit.edu/registrar/calendars'

        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # The first <strong> tag should be the title, e.g. "Spring 2024 Academic Calendar"
            # This is a point of failure if anything changes at the Academic Calendar site, watch closely
            first_strong_tag = soup.find('strong')
            
            if first_strong_tag:
                split = first_strong_tag.text.split()
                # This feels wrong
                mapping = {
                    'spring': SemesterType.SPRING,
                    'fall': SemesterType.FALL,
                    'summer': SemesterType.SUMMER,
                    'winter': SemesterType.WINTER
                }
                sem = mapping[split[0].lower()]
                year = int(split[1])
                
                code = NJIT.term_code(year, sem)
                NJIT._cterm = (code, time.time())
                return code
            else:
                NJIT._cterm[1] = -1 # Ensure that we retry
                if prev_result != None:
                    return prev_result
                else:
                    return None
        else:
            raise Exception(f"Failed to get calendar page (Error {response.status_code})")

    @staticmethod
    def is_current_term(term: str) -> bool:        
        return term == NJIT.current_term()

    # cond_func will only allow a cache lookup when true, so is_current_term needs to be inversed
    # This way we only run this repeatedly for the most recent semester and nothing else
    @staticmethod
    @cond_cache_to_mongodb(db_name="Schedule_Builder", collection_name="Subjects", cond_func=lambda x: not NJIT.is_current_term(x))
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
        
        return [x['SUBJECT'] for x in response.json()]
    
    # cond_func will only allow a cache lookup when true, so is_current_term needs to be inversed
    # This way we only run this repeatedly for the most recent semester and nothing else
    @staticmethod
    @cond_cache_to_mongodb(db_name="Schedule_Builder", collection_name="Bulk_Sections", cond_func=lambda x, _: not NJIT.is_current_term(x))
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
    
    @staticmethod
    def format_course_code(course_code) -> str:
        formatted_code = re.sub(r'(R\d{3}|[A-Za-z]+)(\d+[A-Za-z]?)', r'\1 \2', course_code)
        return formatted_code

    @staticmethod
    def split_course_code(course_code) -> str:
        formatted_code = re.match(r'(R\d{3}|[A-Za-z]+)(\d+[A-Za-z]?)', course_code)
        if formatted_code == None:
            return course_code, ""
        return formatted_code.group(1), formatted_code.group(2)
    
    @staticmethod
    def get_course_desc(course_code: str) -> str:
        if not ' ' in course_code:
            course_code = NJIT.format_course_code(course_code)
        
        cs = course_code.split()
        url = f"https://catalog.njit.edu/ribbit/index.cgi?page=getcourse.rjs&code={cs[0]}%20{cs[1]}"
        
        response = requests.get(url=url)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get description of course {course_code}")
        
        desc = _xml_to_raw_text(response.text)
        return desc
        
if __name__ == "__main__":
    print(SemesterType(78))
    # Code that looks at all professors that have taught a specific course over time
    # Not relevant to the rest of the file, should be deleted at some point
    # import time
    # year = 2024
    # while year > 2010:
    #     for sem in [SemesterType.SPRING, SemesterType.SUMMER, SemesterType.FALL, SemesterType.WINTER]:
    #         term = NJIT.term_code(year, sem)
    #         sections = NJIT.get_sections(term, "CS")
            
    #         profs = set()
            
    #         for sec in sections:
    #             if sec['COURSE'] == 'CS482':
    #                 profs.add(sec['INSTRUCTOR'])
            
    #         print(f"[{year}, {sem}]: {list(profs)}")
    #         time.sleep(2)
            
            
    #     year -= 1
            