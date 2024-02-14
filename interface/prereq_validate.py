import networkx as nx
import matplotlib.pyplot as plt
import re
from pyvis.network import Network

from .utils import mongo_client

db = mongo_client["NJIT_Course_API"]
course_collection = db["Courses"]

# course = course_collection.find_one({'_id': 'IS 465'})
# prereqs = course['courseInformation']['courses'][0]['prerequisites']

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

def desc(course):
    return " ".join(course['courseInformation']['courses'][0]['descriptionAdditional'])

class Node():
    def __init__(self, name, dependency):
        self.name = name
        self.dependency = dependency

class CourseDependencyGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def process_name(self, name: str):
        if isinstance(name, list):
            return [self.process_name(x) for x in name]
        name = name.replace("(", "")
        name = name.replace(")", "")
        return name.strip()
    
    def add_node(self, node):
        # Split dependencies into individual courses or expressions
        #dependencies = self.parse_dependencies(node.dependency)

        # Add edges based on dependencies
        dep_tree = self.build_parse_tree(self.shunting_yard_modified(node.dependency))
        self.dep_to(node.name, self.order_dep_tree(dep_tree))
    
    def order_dep_tree(self, dep: list | str):
        if isinstance(dep, list):
            if len(dep) == 2:
                # Shouldn't happen but these are cases like ['&', 'A']
                return self.order_dep_tree(dep[1])
            processed_list = set([self.order_dep_tree(x) for x in dep[1:]])
            return tuple([dep[0]] + sorted(list(processed_list), key=str))
        else:
            return dep
    
    def dep_to(self, target, dep: tuple | str):
        if dep == None:
            return
        if isinstance(dep, tuple):
            if len(dep) == 2:
                self.dep_to(target, dep[1])
                return
            if dep[0] == '&':
                processed_list = [str(x) for x in dep[1:]]
                processed_list = sorted(list(set(processed_list)))
                and_node = f"AND_{'_'.join(processed_list)}"
                if len(processed_list) == 1:
                    self.graph.add_edge(processed_list[0], target)
                    return
                for d in dep[1:]:
                    self.dep_to(and_node, d)
                self.graph.add_edge(and_node, target)
            elif dep[0] == '|':
                processed_list = [str(x) for x in dep[1:]]
                processed_list = sorted(list(set(processed_list)))
                if len(processed_list) == 1:
                    self.graph.add_edge(processed_list[0], target)
                    return
                or_node = f"OR_{'_'.join(processed_list)}"
                for d in dep[1:]:
                    self.dep_to(or_node, d)
                self.graph.add_edge(or_node, target)
            else:
                # should never happen but we handle it just in case
                # treat as implicit and
                for d in dep:
                    self.dep_to(target, d)
                ...
        else: # str
            self.graph.add_edge(dep, target)
                
    def tokenize(self, expression):
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

    def shunting_yard_modified(self, expression):
        self.precedence = {'|': 2, '&': 1}
        tokens = self.tokenize(expression)
        output = []
        operators = []

        for token in tokens:
            if token not in self.precedence and token not in ['(', ')']:
                output.append(token)
            elif token in self.precedence:
                while operators and operators[-1] in self.precedence and \
                        self.precedence[operators[-1]] >= self.precedence[token]:
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

    def build_parse_tree(self, postfix_expression):
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

    
    def add_edges(self, course, dependency):
        if isinstance(dependency, list):  # OR condition
            or_node = f"OR_{'_'.join(dependency)}"
            self.graph.add_node(or_node, style='invis')  # Invisible OR node
            for d in dependency:
                self.graph.add_edge(d, or_node)
                self.graph.add_edge(or_node, course)
        else:  # AND condition
            self.graph.add_edge(dependency, course)

    def _visualize_graph(self):
        pos = nx.spectral_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True)
        plt.show()

    def visualize_graph_nohier(self, filename='graph.html'):
        net = Network(notebook=True, directed=True)

        # Add nodes and edges to the Pyvis network
        for node in self.graph.nodes:
            if node.startswith("OR_"):
                # Make OR nodes small and a different color
                net.add_node(node, label='', title=node, color='#CCFFD0', size=5, font={'size':0})
            elif node.startswith("AND_"):
                # Make OR nodes small and a different color
                net.add_node(node, label='', title=node, color='#ffcccb', size=5, font={'size':0})
            else:
                net.add_node(node, label=node, title=node)

        for edge in self.graph.edges:
            net.add_edge(edge[0], edge[1], arrows='to')

        # Set options for better appearance
        net.set_options("""
        var options = {
          "nodes": {
            "shape": "dot",
            "size": 15
          },
          "edges": {
            "smooth": {
              "type": "continuous"
            },
            "color": {
              "inherit": true
            },
            "arrows": {
              "to": { "enabled": true, "scaleFactor": 0.5 }
            }
          },
          "physics": {
            "forceAtlas2Based": {
              "springLength": 100
            },
            "minVelocity": 0.75,
            "solver": "forceAtlas2Based"
          },
          "interaction": {
            "tooltipDelay": 200,
            "hideEdgesOnDrag": false
          }
        }
        """)

        # Save or show graph
        net.show(filename)
        
    
tree = CourseDependencyGraph()

#print(tree.build_parse_tree(tree.shunting_yard_modified("CS 100 & (CS 113 | CS 115 | MATH 333 | MATH 341)")))
elements = [['Label', 'Type', 'Tags']]
connections = [['From', 'To', 'Direction', 'Type', 'Tags']]

for course in course_collection.find({}):
    e = reqs_to_str(course)
    node = Node(course['_id'], dependency=e)
    tree.add_node(node)

#tree.visualize_graph_nohier()

import csv
for node in tree.graph.nodes:
    tags = ""
    type = ""
    if node.startswith("OR_"):
        # Make OR nodes small and a different color
        tags = f"operator | OR"
        type = "operator"
    elif node.startswith("AND_"):
        # Make OR nodes small and a different color
        tags = f"operator | AND"
        type = "operator"
    else:
        tags = f"course | {node.split()[0]}"
        type = "course"
    elements.append([node, type, tags])

for c in tree.graph.edges:
    type = ""
    tags = ""
    if c[1].startswith("OR_"):
        type = "OR_dep"
    else:
        type = "AND_dep"
    
    connections.append([c[0], c[1], 'directed', type, tags])

with open('elements.csv','w+') as myfile:
  wr = csv.writer(myfile) #, quoting=csv.QUOTE_ALL)
  wr.writerows(elements)
  
with open('connections.csv','w+') as myfile:
  wr = csv.writer(myfile) #, quoting=csv.QUOTE_ALL)
  wr.writerows(connections)