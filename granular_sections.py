from interface.NJIT import NJIT, SemesterType
from interface.utils import mongo_client

year = 2021


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
                                crns[section['CRN']]['TIMES'][d].append(section['TIMES'])
                    continue

                section['COURSE'] = NJIT.format_course_code(section['COURSE'])
                course_number = section['COURSE'].split(' ')[-1]
                section['SUBJECT'] = section['COURSE'].split(' ')[0]
                
                if course_number[0].isdigit():
                    section['COURSE_LEVEL'] = int(course_number[0])
                else:
                    section['COURSE_LEVEL'] = None
                
                if not 'online' in (section.get('INSTRUCTION_METHOD') or 'online').lower() and len((section.get('LOCATION') or '').strip()) > 0:
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
                        'S': False
                    }
                    for d in section['DAYS']:
                        day_obj[d] = True
                    section['DAYS'] = day_obj
                
                    if section['TIMES'] != None:
                        time_obj = {}
                        for d in section['DAYS']:
                            time_obj[d] = [section['TIMES']]
                        section['TIMES'] = time_obj
                    
                # Flags
                section['IS_HONORS'] = section['SECTION'][0] == 'H'
                section['IS_ONLINE'] = section['SECTION'][0] in ['4', '8']
                section['IS_OFF_HOURS'] = section['SECTION'][0] == '1'
                
                # Summer Periods
                if sem == SemesterType.SUMMER and len(section['SECTION']) > 2:
                    section['SUMMER_PERIOD'] = section['SECTION'][1] if section['SECTION'][1] in ['1', '2', '4'] else None
                else:
                    section['SUMMER_PERIOD'] = None                
                
                section['_id'] = f"{term}-{section['CRN']}"
                crns[section['CRN']] = section
            
            for section in crns.values():
                col.replace_one({'_id':f"{term}-{section['CRN']}"}, section, upsert=True)
            print(f"[{year}; {sem}]: {subject} ({len(crns)})")
    year -= 1
                