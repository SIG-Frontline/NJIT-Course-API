import re
import json

import requests

import xml.etree.ElementTree as ET

from utils import openai_client, cache_to_mongodb

def xml_to_raw_text(xml_string) -> str:
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

@cache_to_mongodb(db_name="NJIT_Course_API", collection_name="LLM_Cache")
def llm(prompt: str, json_mode: bool = True, model: str = "gpt-4-1106-preview") -> dict | str:
    global openai_client
    
    format = {"type": "json_object"} if json_mode else {'type':'text'}
    completion = openai_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": prompt}
        ],
        model=model,
        response_format=format
    )
    
    content = completion.choices[0].message.content
    if json_mode:
        return json.loads(content)
    else:
        return content

def format_course_code(course_code) -> str:
    # Use regular expression to add a space between letters and digits
    formatted_code = re.sub(r'(R\d{3}|[A-Za-z]+)(\d+)', r'\1 \2', course_code)
    return formatted_code

def get_course_desc(course_code: str) -> str:
    if not ' ' in course_code:
        course_code = format_course_code(course_code)
    
    cs = course_code.split()
    url = f"https://catalog.njit.edu/ribbit/index.cgi?page=getcourse.rjs&code={cs[0]}%20{cs[1]}"
    
    response = requests.get(url=url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to get description of course {course_code}")
    
    desc = xml_to_raw_text(response.text)
    return desc

def get_course_reqs(course_code: str):
    desc = get_course_desc(course_code)
    
    spec = ""
    with open("course_specification.md", 'r') as reader:
        spec = reader.read()
    
    prompt = f"""{spec}

---------------

Consider the above specification for defining course requirements. Format the requirements of the course described in the following XML text into this format.
Respond in JSON only as specified.

{desc}
"""

    return llm(prompt=prompt)

if __name__ == "__main__":
    print(get_course_reqs("CS 490"))