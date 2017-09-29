#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import re
import ply.yacc as yacc
import ply.lex as lex
from itertools import cycle


class SecRule():
    """ This is a class to break up components of SecRule declarations
    """
    def __init__(self, rule=None, variable=None, operator=None,
                 action=None, chain_rule=None):
        """!@brief Creates a secrule object. It contains objects for the Variable,
        Operator, and Action parts of the rules

        @param rule A string containing the full SecRule
        @param variable A LexToken object with a type = variable
        @param operator A LexToken object with a type = operator
        @param action An Action object associated with the rule
        @param chain_rule A SecRule object that is the next rule in a chain
        (if there is a chain action in this rule)
        """
        self.rule = rule
        self.variable = variable
        self.operator = operator
        self.action = action
        # if the rule is a chain rule, store the next rule here
        self.chain_rule = chain_rule

    def jsonify_rule(self):
        """!@brief Returns a dict of the attributes of the object
        """
        json_rule = {}
        json_rule['rule'] = self.rule
        json_rule['variable'] = self.variable.value
        json_rule['operator'] = self.operator.value
        json_rule['action'] = self.action.action
        if self.chain_rule is not None:
            json_rule['chain_rule'] = self.chain_rule.jsonify_rule()
        return json_rule

    def print_json_rule(self):
        """!@brief Prints the rule in a json format
        """
        print(json.dumps(self.jsonify_rule(), sort_keys=True, indent=4,
                         separators=(',', ': ')))


class Action():
    """!@brief A class to represent the 'action' component of a SecRule
    declaration
    """
    def __init__(self, action=None):
        """!@brief The constructor for Action objects

        Rules that have a 'chain' action will have a chain_rule attribute in
        the associated SecRule object

        @param action A string containing the action component of a SecRule
        """
        # if the rule does not start with a single or double quote, then add
        # the whole line, else grab the line between the quotes
        if action[0] == '"' or action[0] == '\'':
            # grab line between quotes
            self.action = action[1:-1].split(',')
        else:
            # grab whole line
            self.action = action.split(',')


class Parser():
    """!@brief A class to handle parsing ModSecurity rules
    """
    def __init__(self, rule_string=""):
        """!@brief A constructor for creating a Parser object

        @param rule_string A string containing a rule to be parsed
        """
        self.rule_string = rule_string

    def parse(self):
        """!@brief Parses the rule_string in this object and returns an
        associated SecRule object
        """
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

        def t_OPERATOR(t):
            # figure out how to get the cap. group to not grab the last space
            r'(\"@?.*?\")\s+?'
            for i in t.lexer.lexmatch.groups():
                if i is not None and 'SecRule' not in i:
                    t.value = i.lstrip().rstrip()
                    return t
                else:
                    # if unable to parse an operator, set it to None
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

            # return the full SecRule object
            if hasattr(newrule, 'variable') and \
               newrule.variable is not None and \
               hasattr(newrule, 'operator') and \
               newrule.operator is not None and \
               hasattr(newrule, 'action') and newrule.action is not None:
                # add the rule string to the SecRule object
                newrule.rule = self.rule_string
                return newrule


def chain_rules(secrules):
    """!@brief Loop through a list of secrules in order to chain rules together
    @param secrules A list of SecRule objects
    """
    i = 0       # index

    while i < len(secrules):
        beg_chain = i       # index of the beginning of a chain rule
        end_chain = None
        if 'chain' in secrules[beg_chain].action.action:
            # loop through all the rules to find the end of the chain
            for index in range(beg_chain, len(secrules)):
                if 'chain' in secrules[index].action.action and \
                   secrules[index].chain_rule is None:
                    # continue through loop if the rule is part of the chain
                    continue
                else:
                    # else, we are at the end of the chain
                    end_chain = index
                    break

            # start at end of chain and add to the chain_rule attribute of the
            # element before it
            if end_chain is not None and end_chain > beg_chain:
                for num in range(end_chain, beg_chain, -1):
                    secrules[num-1].chain_rule = secrules[num]
                    del secrules[num]

        i += 1
    return secrules


def parse_file(rulefile):
    """!@brief Parse a given file containing ModSecurity rules
    @param rulefile The name of a file containing the rules to parse
    """
    data = ""       # variable to hold string of the contents of the rule file
    seccomponentsignature = ""  # signature for the version of the rules
    secrules = []   # list of SecRule objects
    plaintextrules = []     # list of lines from a file containing rules
    plaintextactions = []   # list of SecAction declarations
    plaintextmarkers = []   # list of SecMarker declarations

    with open(rulefile, 'r') as f:
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
                    # exit status 1 here
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

    # parse the list of rules, if they have a chain, add it to the chain rule
    # of the previous rule
    chained_rules = chain_rules(secrules)

    for index, secrule in enumerate(chained_rules):
        # print the json version of the rule
        secrule.print_json_rule()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse ModSecurity Rules')
    parser.add_argument('--file', dest='rulefile', required=True,
                        help='the file containing a list of ModSecurity rules \
                        to parse')

    args = parser.parse_args()
    parse_file(args.rulefile)
