#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import re
import ply.yacc as yacc
import ply.lex as lex
from itertools import cycle


class SecRule():
    """ A class for a secrule. It contains objects for the Variable,
    Operator, and Action parts of the rules """
    def __init__(self, rule=None, variable=None, operator=None,
                 action=None, chain_rule=None):
        self.rule = rule
        self.variable = variable
        self.operator = operator
        self.action = action
        # if the rule is a chain rule, store the next rule here
        self.chain_rule = chain_rule


class Variable():
    def __init__(self, variable):
        pass


class Operator():
    """ Operators begin with the @ character """
    def __init__(self, operator):
        pass


class Action():
    # if the action is a 'chain' then the subsequent SecRule is also part of
    # the one being evaluated
    def __init__(self, action=None):
        self.action = action[1:-1].split(',')


class Parser():
    def __init__(self, rule_string=""):
        self.rule_string = rule_string

    def parse(self):
        newrule = SecRule()

        # List of token names.
        tokens = (
          'SECMARKER',
          'SECCOMPONENTSIGNATURE',
          'SECRULE',
          'SECACTION',
          'SPACE',
          'VARIABLE',
          'OPERATOR',
          'ACTION',
          'BACKSLASH',
        )

        # Regular expression rules for simple tokens
        t_SECRULE = r'SecRule'
        t_BACKSLASH = r'\\'
        t_SECACTION = r'SecAction'

        def t_SECMARKER(t):
            r'\s*?SecMarker.*'
            return t

        def t_SECCOMPONENTSIGNATURE(t):
            r'\s*?SecComponentSignature.*'
            return t

        def t_OPERATOR(t):
            r'\"@.*?\"'
            return t

        def t_VARIABLE(t):
            r'SecRule\s(.*?)\s'
            # pull out all groups that match the regex, loop through them and
            # store the group that does not contain SecRule and is not None
            for i in t.lexer.lexmatch.groups():
                if i is not None and 'SecRule' not in i:
                    t.value = i
                    return t
                else:
                    # if unable to parse a variable, set it to None
                    t.value = None
            return t

        def t_ACTION(t):
            r'\"?(.+)\"?'
            # pull out all groups that match the regex, loop through them and
            # store the group that does not contain SecRule and is not None
            for i in t.lexer.lexmatch.groups():
                if i is not None and 'SecRule' not in i:
                    t.value = i
                    return t
                else:
                    # if unable to parse an action, set it to None
                    t.value = None
            return t

        # Define a rule so we can track line numbers
        def t_newline(t):
            r'\n+'
            t.lexer.lineno += len(t.value)

        # A string containing ignored characters (spaces and tabs)
        t_ignore = '\t '

        # Error handling rule
        def t_error(t):
            print("Illegal character '%s'" % t.value[0])
            t.lexer.skip(1)

        # Build the lexer
        lexer = lex.lex()

        # Give the lexer some input
        lexer.input(self.rule_string)

        # Tokenize
        while True:
            tok = lexer.token()
            if not tok:
                break      # No more input

            elif tok.type == 'VARIABLE':
                newrule.variable = tok

            elif tok.type == 'OPERATOR':
                newrule.operator = tok

            elif tok.type == 'ACTION':
                rule_action = Action(tok.value)
                newrule.action = rule_action
                print(tok)

            # return the full SecRule object
            if hasattr(newrule, 'variable') and \
               newrule.variable is not None and \
               hasattr(newrule, 'operator') and \
               newrule.operator is not None and \
               hasattr(newrule, 'action') and newrule.action is not None:
                # add the rule string to the SecRule object
                newrule.rule = self.rule_string
                return newrule


def parse_file(rulefile):
    data = ""       # variable to hold string of the contents of the rule file
    seccomponentsignature = ""  # signature for the version of the rules
    secrules = []   # list of SecRule objects
    plaintextrules = []     # list of lines from a file containing rules
    plaintextactions = []   # list of SecAction declarations
    plaintextmarkers = []   # list of SecMarker declarations

    with open(args.rulefile, 'r') as f:
        # for every line in the file, check to see if it is blank or
        # check if it does not start with SecRule
        # Declaration types supported:
        #       SecRule, SecAction, SecMarker, SecComponentSignature
        for index, line in enumerate(f):
            first_char_index = len(line) - len(line.lstrip())
            # if the line is empty or starts with a #, don't parse it
            if len(line) == 1:
                next

            # if the line has whitespace chars but is empty (ex. \t\t\n)
            elif len(line.lstrip()) == 0:
                next

            # if the line starts with a comment, skip
            elif line[first_char_index] == '#':
                next

            # if the line is a SecAction or SecMarker, add it to the string
            elif 'SecAction' in line or 'SecMarker' in line:
                data += line.lstrip().rstrip()

            # if the line does not match any of the previous criteria, it is a
            # valid rule line
            elif line.rstrip()[-1:] == '\\':
                data += line.lstrip().rstrip()[:-1]

            # else, add the line to the rest of the data
            else:
                data += line.lstrip().rstrip()
                if 'SecAction' in data:
                    plaintextactions.append(data.lstrip().rstrip())
                elif 'SecRule' in data:
                    plaintextrules.append(data.lstrip().rstrip())
                elif 'SecMarker' in data:
                    plaintextmarkers.append(data.lstrip().rstrip())
                elif 'SecComponentSignature' in data:
                    seccomponentsignature = data
                else:
                    print('Parsing Error, message: \n---\n' + data + '\n---')
                    #print("There was an error parsing something somewhere...")
                data = ""

    # for all the rules in the plaintext rules list, create a SecRule object
    # and add it to a SecRules list
    for rule in plaintextrules:
        secrule = SecRule()
        p = Parser(rule)
        secrule = p.parse()     # parse the rule string and return SecRule obj
        # append the SecRule object to the object list
        if secrule is not None:
            secrules.append(secrule)

    for index, secrule in enumerate(secrules):
        if 'chain' in secrule.action.action:
            # add the next rule in the secrules list to secrule.chain_rule
            # then remove the next element in the list
            secrule.chain_rule = secrules[index+1]
            del secrules[index+1]

    for index, rule in enumerate(secrules):
        #print(str(index) + ': ' + str(rule.__dict__))
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse ModSecurity Rules')
    parser.add_argument('--file', dest='rulefile', required=True,
                        help='the file containing a list of ModSecurity rules \
                        to parse')

    args = parser.parse_args()
    #import pdb; pdb.set_trace()
    parse_file(args.rulefile)
