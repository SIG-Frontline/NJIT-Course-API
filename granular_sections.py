from interface.NJIT import NJIT, SemesterType
from interface.utils import mongo_client
import time
from datetime import datetime

year = 2024


db = mongo_client['Schedule_Builder']
col = db['Sections']

while year > 2010:
    for sem in [SemesterType.SPRING, SemesterType.SUMMER, SemesterType.FALL, SemesterType.WINTER]:
        term = NJIT.term_code(year, sem)
        for subject in NJIT.get_subjects(term):
            time.sleep(0.5)
            sections = NJIT.get_sections(term, subject)
            
            crns = {}
            
            for section in sections:
                assert isinstance(section, dict)
                
                del section['ROW_NUMBER']
                
                # Flags
                section['IS_HONORS'] = section['TITLE'].lower().endswith('honors')
                section['IS_ASYNC'] = 'online' in (section.get('INSTRUCTION_METHOD') or '').lower()
                
                if section['DAYS'] != None:
                    day_obj = {
                        'M': False,
                        'T': False,
                        'W': False,
                        'R': False,
                        'F': False,
                        'S': False,
                        'U': False
                    }
                    for d in section['DAYS']:
                        day_obj[d] = True
                    section['DAYS'] = day_obj
                    
                    if section['TIMES'] != None:
                        times = section['TIMES'].split(' - ')
                        try:
                            times = [datetime.strptime(x, '%I:%M %p') for x in times]
                        except ValueError:
                            # Time is probably 'TBA' or something, leave it empty
                            section['TIMES'] = []
                        else:
                            section['TIMES'] = []
                            day_str = ''
                            for k, v in day_obj.items():
                                if v:                                    
                                    time_obj = {
                                        'day': k,
                                        'start': times[0],
                                        'end': times[1]
                                    }               
                                    if not section['IS_ASYNC'] and len((section.get('LOCATION') or '').strip()) > 0:                                
                                        s = section['LOCATION'].split(' ')
                                        time_obj['building'] = s[0]
                                        time_obj['room'] = ' '.join(s[1:])
                                    else:
                                        time_obj['building'] = None
                                        time_obj['room'] = None
                                    section['TIMES'].append(time_obj)
                    else:
                        section['TIMES'] = []                  
                else:
                    section['DAYS'] = None
                    section['TIMES'] = []
                del section['LOCATION']
                
                if section['CRN'] in crns:
                    if section['DAYS'] != None:
                        for d in section['DAYS']:
                            crns[section['CRN']]['DAYS'][d] = True
                        
                        crns[section['CRN']]['TIMES'].extend(section['TIMES'])
                    continue

                section['COURSE'] = NJIT.format_course_code(section['COURSE'])
                course_number = section['COURSE'].split(' ')[-1]
                section['SUBJECT'] = section['COURSE'].split(' ')[0]
                
                if course_number[0].isdigit():
                    section['COURSE_LEVEL'] = int(course_number[0])
                else:
                    section['COURSE_LEVEL'] = None
                
                section['MAX'] = int(section['MAX'])
                section['NOW'] = int(section['NOW'])              
                
                try:         
                    comment_list = section['COMMENTS'].split('<br />')
                    comment_list = [x.lower() for x in comment_list]
                except:
                    comment_list = []
                            
                # Summer Periods
                if any(c.startswith('full summer') for c in comment_list):
                    section['SUMMER_PERIOD'] = 4
                elif any(c.startswith('first summer') for c in comment_list):
                    section['SUMMER_PERIOD'] = 1
                elif any(c.startswith('second summer') for c in comment_list):
                    section['SUMMER_PERIOD'] = 2
                else:
                    section['SUMMER_PERIOD'] = None
                # if sem == SemesterType.SUMMER and len(section['SECTION']) > 2:
                #     section['SUMMER_PERIOD'] = section['SECTION'][1] if section['SECTION'][1] in ['1', '2', '4'] else None
                # else:
                #     section['SUMMER_PERIOD'] = None                
                
                section['_id'] = f"{term}-{section['CRN']}"
                crns[section['CRN']] = section
            
            for section in crns.values():
                col.replace_one({'_id':f"{term}-{section['CRN']}"}, section, upsert=True)
            print(f"[{year}; {sem}]: {subject} ({len(crns)})")
    year -= 1
                