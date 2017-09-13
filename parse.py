#!/usr/bin/python3
# ARG1: Name of the file containing a list of rules

import sys
import string
import ply.yacc as yacc
import ply.lex as lex

class SecRule():
    """ A class for a secrule. It contains objects for the Variable, Operator, 
    and Action parts of the rules """
    def __init__(self, rule):
        self.rule = rule
        self.variable = ""
        self.operator = ""
        self.action = ""

    def get_var(self):
        Variable(self.rule)

    def get_operator(self):
        Operator(self.rule)

class Variable():
    def __init__(self, rule):
        pass

class Operator():
    """ Operators begin with the @ character """
    def __init__(self, rule):
        pass

class Action():
    def __init__(self, rule):
        pass

def last_non_whitespace(line):
   # Get the last character line a line that is not a whitespace character
   reverse_str = line[::-1]
   #print("reverse str: " + reverse_str)
   for char in reverse_str:
       if char not in string.whitespace:
           #print('char isnt whitespace: "' + char + '"')
           return char


if __name__ == '__main__':
    # read rules from test file
    # rules can expand across multiple lines, if the line ends with '\'
    rule = ""
    rules = []

    with open(sys.argv[1], 'r') as f:
        for line in f:
            line = line.strip()
            #for index in range(len(line)-1, 0, -1):
            #    if line[index] not in string.whitespace:
            #        print(line[index], end="")
            # if there is one rule on a line of its own
            if 'SecRule' in line and last_non_whitespace(line) != '\\':
                rules.append(line)

            # if the rule continues onto another line
            elif 'SecRule' in line and last_non_whitespace(line) == '\\':
                rule += line[:-1]

            # if the rule isnt an empty string and the line doesnt end with \
            elif rule != "" and last_non_whitespace(line) == '\\':
                rule += line[:-1]
                #rules.append(rule)

            elif rule != "" and last_non_whitespace(line) != '\\':
                rule += line
                rules.append(rule)
                rule = ""

            else:
                rule = ""

for rule in rules:
    print(rule.strip('\n'))



