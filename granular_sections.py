from interface.NJIT import NJIT, SemesterType
from interface.utils import mongo_client
import time

year = 2024


db = mongo_client['Schedule_Builder']
col = db['Sections']

while year > 2010:
    for sem in [SemesterType.SPRING, SemesterType.SUMMER, SemesterType.FALL, SemesterType.WINTER]:
        term = NJIT.term_code(year, sem)
        for subject in NJIT.get_subjects(term):
            sections = NJIT.get_sections(term, subject)
            
            crns = {}
            
            for section in sections:
                assert isinstance(section, dict)
                
                del section['ROW_NUMBER']
                
                if section['CRN'] in crns:
                    if section['DAYS'] != None:
                        for d in section['DAYS']:
                            crns[section['CRN']]['DAYS'][d] = True
                        if section['TIMES'] != None:
                            for d in section['DAYS']:
                                times = section['TIMES'].split(' - ')
                                times = [time.strptime(x, '%I:%M %p') for x in times]
                                crns[section['CRN']]['TIMES'][d].append(times)
                    continue

                section['COURSE'] = NJIT.format_course_code(section['COURSE'])
                course_number = section['COURSE'].split(' ')[-1]
                section['SUBJECT'] = section['COURSE'].split(' ')[0]
                
                if course_number[0].isdigit():
                    section['COURSE_LEVEL'] = int(course_number[0])
                else:
                    section['COURSE_LEVEL'] = None
                
                
                
                # Flags
                section['IS_HONORS'] = section['TITLE'].lower().endswith('honors')
                section['IS_ASYNC'] = 'online' in (section.get('INSTRUCTION_METHOD') or '').lower()
                
                if not section['IS_ASYNC'] and len((section.get('LOCATION') or '').strip()) > 0:
                    section['BUILDING'] = " ".join(section['LOCATION'].split(' ')[:-1])
                    section['FLOOR'] = section['LOCATION'].split(' ')[-1][0]
                else:
                    section['BUILDING'] = None
                    section['FLOOR'] = None
                
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
                        time_obj = {}
                        for d in section['DAYS']:
                            times = section['TIMES'].split(' - ')
                            times = [time.strptime(x, '%I:%M %p') for x in times]
                            time_obj[d] = [times]
                        section['TIMES'] = time_obj                                    
                
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
                