#from interface import NJIT
from interface.NJIT import SemesterType, NJIT

year = 2024
while year > 2010:
    for sem in [SemesterType.SUMMER]:
        term = NJIT.term_code(year, sem)
        
        sections = NJIT.get_sections(term, 'CS')
        profs = set()
        for s in sections:
            if s['COURSE'] == 'CS114':
                profs.add(s['INSTRUCTOR'])
        print(f"[{year}, {sem}]: {list(profs)}")
    year -= 1
    exit()