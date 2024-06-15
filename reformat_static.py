from interface.NJIT import NJIT, SemesterType
from interface.utils import mongo_client
import time
from datetime import datetime

db = mongo_client['Schedule_Builder']
col = db['Course_Static']

def reqs_to_str(course):
    if len(course['courseInformation']['courses']) == 0:
        return ""
    if 'prerequisites' not in course['courseInformation']['courses'][0]:
        return ""
    prereqs = course['courseInformation']['courses'][0]['prerequisites']
    req_str = ""
    for req in prereqs:
        req_str += req['connector'] + " "
        req_str += req['leftParenthesis'] + " "
        if len(req['subjectCodePrerequisite']) > 0:
            req_str += f" {req['subjectCodePrerequisite']} {req['courseNumberPrerequisite']} "
        else:
            req_str += f"${req['tescCode']}"
        req_str += req['rightParenthesis'] + " "
    req_str = " ".join(req_str.split())
    req_str = req_str.replace(" A ", " & ")
    req_str = req_str.replace(" O ", " | ")
    return req_str

def order_dep_tree(dep: list | str):
    if isinstance(dep, list):
        if len(dep) == 2:
            # Shouldn't happen but these are cases like ['&', 'A']
            return order_dep_tree(dep[1])
        processed_list = set([order_dep_tree(x) for x in dep[1:]])
        return tuple([dep[0]] + sorted(list(processed_list), key=str))
    else:
        return dep
            
def tokenize(expression):
    tokens = []
    buffer = ""
    for char in expression:
        if char.isalpha() or char.isdigit() or char == ' ':
            buffer += char  # Build up the identifier
        else:
            if buffer.strip():
                tokens.append(buffer.strip())  # Add the completed identifier
                buffer = ""
            if char in ['&', '|', '(', ')']:
                tokens.append(char)  # Add the operator or parenthesis
    if buffer.strip():
        tokens.append(buffer.strip())  # Add any remaining identifier
    return tokens

def shunting_yard_modified(expression):
    precedence = {'|': 2, '&': 1}
    tokens = tokenize(expression)
    output = []
    operators = []

    for token in tokens:
        if token not in precedence and token not in ['(', ')']:
            output.append(token)
        elif token in precedence:
            while operators and operators[-1] in precedence and \
                    precedence[operators[-1]] >= precedence[token]:
                output.append(operators.pop())
            operators.append(token)
        elif token == '(':
            operators.append(token)
        elif token == ')':
            while operators and operators[-1] != '(':
                output.append(operators.pop())
            operators.pop()

    while operators:
        output.append(operators.pop())

    return output

def build_parse_tree(postfix_expression):
    stack = []
    for token in postfix_expression:
        if token not in ['&', '|']:
            # Token is an operand, create a leaf node
            stack.append(token)
        else:
            # Token is an operator, pop two nodes and make them children
            node = [token]
            if stack: 
                right = stack.pop()
                if isinstance(right, list) and right[0] == token:
                    node.extend(right[1:])
                else:
                    node.append(right)

            if stack: 
                left = stack.pop()
                if isinstance(left, list) and left[0] == token:
                    node.extend(left[1:])
                else:
                    node.append(left)              

            stack.append(node)
    return stack.pop() if stack else None

for course in col.find({}):
    if 'courseInput' not in course:
        # Already restructured, skip
        continue
    rebuilt = {
        '_id':course['_id'],
        'prereq_str':reqs_to_str(course)
    }
    if len(course['courseInformation']['courses']) == 0:
        col.delete_one({'_id':course['_id']})
        continue
    data = course['courseInformation']['courses'][0]
    rebuilt['description'] = ''.join(data.get('descriptionAdditional',[]))
    rebuilt['subject'] = data['subjectCode']
    rebuilt['course_number'] = data['courseNumber']
    
    tree = build_parse_tree(shunting_yard_modified(rebuilt['prereq_str']))
    rebuilt['tree'] = tree
    
    col.replace_one({'_id':course['_id']}, rebuilt)
    