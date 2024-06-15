import json

def parse_condition(condition):
    if 'relationalOperator' in condition:
        if condition['relationalOperator']['left'] == '-COURSE-':
            courses = [f"{c['discipline']}{c['number']}" if 'numberEnd' not in c else f"{c['discipline']}{c['number']}-{c['numberEnd']}" for c in condition['relationalOperator']['courseArray']]
            if len(courses) == 1:
                condition['relationalOperator']['left'] = courses[0]
            else:
                condition['relationalOperator']['left'] = '[ ' + ' AND '.join(courses) + ' ]'

        return f"{condition['relationalOperator']['left']} {condition['relationalOperator']['operator']} {condition['relationalOperator']['right']}"
    elif 'classCreditOperator' in condition:
        courses = [f"{c['discipline']}{c['number']}" if 'numberEnd' not in c else f"{c['discipline']}{c['number']}-{c['numberEnd']}" for c in condition['courseArray']]
        connector = {condition['connector']} + ' '
        return f"{condition['classCreditOperator']} [ {connector.join(courses)} ]"
    elif 'connector' in condition:
        if 'leftCondition' in condition and not 'rightCondition' in condition:
            return parse_condition(condition['leftCondition'])
        if 'rightCondition' in condition and not 'leftCondition' in condition:
            return parse_condition(condition['rightCondition'])
            
        return f"({parse_condition(condition['leftCondition'])}) {condition['connector']} ({parse_condition(condition['rightCondition'])})"
    raise NotImplementedError()

def parse_rule(rule, indent=0):
    result = ""    
    if 'ruleType' not in rule:
        if 'catalogYear' in rule:
            # Degree block
            result += f"{'  ' * indent}{rule['requirementType']}-{rule['requirementValue']}:\n"
            result += parse_rule_array(rule['ruleArray'], indent+1)
        else:
            raise NotImplementedError()
    elif rule['ruleType'] == 'IfStmt':
        # Processing the IF condition
        condition = rule['requirement']
        left_condition = parse_condition(condition['leftCondition'])
        #right_condition = parse_condition(condition['rightCondition'])
        if_stmt = f"{'  ' * indent}IF {left_condition}:\n"
        result += if_stmt

        # Processing the ifPart
        if 'ifPart' in rule['requirement']:
            result += parse_rule_array(rule['requirement']['ifPart']['ruleArray'], indent + 1)
        
        # Processing the elsePart
        if 'elsePart' in rule['requirement']:
            else_stmt = f"{'  ' * indent}ELSE:\n"
            result += else_stmt
            result += parse_rule_array(rule['requirement']['elsePart']['ruleArray'], indent + 1)

    elif rule['ruleType'] == 'Course':       
        courses = rule['requirement']['courseArray']
        if 'classCreditOperator' in rule['requirement']:
            course_str = f" {rule['requirement']['classCreditOperator']} ".join([f"{course['discipline']} {course['number']}" for course in courses])
        else:
            course_str = "[" + ", ".join([f"{course['discipline']} {course['number']}" for course in courses]) + "]"
        
        # Credits or Classes requirement
        if 'classesBegin' in rule['requirement'] and rule['requirement']['classesBegin'] != '1':
            if int(rule['requirement']['classesBegin']) == len(courses):
               course_str = f" AND ".join([f"{course['discipline']} {course['number']}" for course in courses]) 
            else:
                course_str = f"Choose {rule['requirement']['classesBegin']}: {course_str}"
        elif 'creditsBegin' in rule['requirement']:
            course_str = f"{rule['requirement']['creditsBegin']} Credits of: {course_str}"
        
        course_stmt = f"{'  ' * indent}{course_str}\n"
        result += course_stmt
    elif rule['ruleType'] == 'Subset':
        result += f"{'  ' * indent}SUBSET \"{rule['label']}\" ({rule['labelTag']}):\n"
        result += parse_rule_array(rule['ruleArray'], indent+1)        
    elif rule['ruleType'] == 'Complete' or rule['ruleType'] == 'Incomplete':
        result += f"{'  ' * indent}{rule['ruleType'].upper()}: \"{rule['label']}\" ({rule['labelTag']})\n"
    elif rule['ruleType'] == 'Block':
        result += f"{'  ' * indent}Block(s): {rule['requirement']['type']}-{rule['requirement']['value']} ({rule['requirement']['numBlocks']} blocks)\n"
    elif rule['ruleType'] == 'Blocktype':
        result += f"{'  ' * indent}BlockType(s): {rule['requirement']['type']} x {rule['requirement']['numBlocktypes']}\n"
    elif rule['ruleType'] == 'Group':
        result += f"{'  ' * indent}Group \"{rule['label']}\" ({rule['labelTag']}):\n"
        result += parse_rule_array(rule['ruleArray'], indent+1)
    else:
        raise NotImplementedError()

    return result

def parse_rule_array(rule_array, indent=0):
    result = ""
    for rule in rule_array:
        print(result)
        result += parse_rule(rule, indent)
    return result

data = json.load(open('GEN_SL.json'))

rule = parse_rule_array(data['blockArray'])
with open('output.txt', 'w') as writer:
    writer.write(rule)