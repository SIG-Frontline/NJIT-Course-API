from flask import Blueprint, jsonify, request, abort, url_for
from interface.NJIT import NJIT, SemesterType
from markupsafe import escape

api = Blueprint('api', __name__, url_prefix='/api')

def validate_termcode(term_code: str):
    if len(term_code) != 6:
        return False, "Longer than 6 chars"
    
    for c in term_code:
        if not c.isdigit():
            return False, "Not all digits"
    
    try:
        SemesterType(int(term_code[-2:]))
    except ValueError:
        return False, f"Not a valid semester. Must be one of {list(SemesterType._value2member_map_.keys())}"
    
    return True, ""

@api.route('/current_term')
def current_term():
    return jsonify(term = NJIT.current_term())

# More complex than first thought, revisit later
# @api.route('/term_code')

@api.route("subjects")
def get_subjects():
    term = request.args.get('term')
    valid, desc = validate_termcode(str(term))
    if not valid:
        abort(422, description=f"Invalid Term Code.\nYou can get the term code for the current semester at {url_for('api.current_term')}.\nReason: {desc}\nRefer to the docs for details on term code formatting.")
    return jsonify(subjects = [x['SUBJECT'] for x in NJIT.get_subjects(str(term))])

@api.route('sections')
def get_sections():
    term = request.args.get('term')
    subject = request.args.get('subject')
    
    valid, desc = validate_termcode(term)
    if not valid:
        abort(422, description=f"Invalid Term Code.\nYou can get the term code for the current semester at {url_for('api.current_term')}.\nReason: {desc}\nRefer to the docs for details on term code formatting.")
        
    return jsonify(sections = NJIT.get_sections(term, subject.upper()))

@api.route('course_description')
def get_course_desc():
    course = request.args.get('course')
    return jsonify(desc = NJIT.get_course_desc(course))
    