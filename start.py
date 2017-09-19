#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import re
import ply.yacc as yacc
import ply.lex as lex

class SecRule():
    class SecRule():
        """ A class for a secrule. It contains objects for the Variable, Operator,
        and Action parts of the rules """
        def __init__(self, rule):
            self.rule = rule
            self.variable = ""
            self.operator = ""
            self.action = ""

        def get_var(self):
            Variable(self.variable)

        def get_operator(self):
            Operator(self.operator)

        def get_action(self):
            Action(self.action)

class Variable():
    def __init__(self, variable):
        pass

class Operator():
    """ Operators begin with the @ character """
    def __init__(self, operator):
        pass

class Action():
    def __init__(self, action):
        pass

class Parser():
    def __init__(self, rule_string=""):
        self.rule_string = rule_string

    def parse(self):
        # List of token names.
        tokens = (
          'SECMARKER',
          'SECRULE',
          'SPACE',
          'VARIABLE',
          'OPERATOR',
          'ACTION',
          'BACKSLASH',
        )

        # Regular expression rules for simple tokens
        t_SECRULE    = r'SecRule'
        t_BACKSLASH  = r'\\'

        def t_SECMARKER(t):
            r'\s*?SecMarker.*'
            return t

        def t_SPACE(t):
            r'(\sTX:)'
            #r'\s'
            return t

        def t_OPERATOR(t):
            r'\"@.*?\"'
            return t

        def t_VARIABLE(t):
            r'SecRule\s(.*?)\s'
            # pull out all groups that match the regex, loop through them and store
            # the group that does not contain SecRule and is not None
            for i in t.lexer.lexmatch.groups():
                if i is not None and 'SecRule' not in i:
                    t.value = i
                    return t
                else:
                    # if unable to parse a variable, set it to None
                    t.value = None
            return t

        def t_ACTION(t):
            r'\"(.*?)\"'
            # pull out all groups that match the regex, loop through them and store
            # the group that does not contain SecRule and is not None
            for i in t.lexer.lexmatch.groups():
                if i is not None and 'SecRule' not in i:
                    t.value = i
                    return t
                else:
                    # if unable to parse a variable, set it to None
                    t.value = None
            return t

        # Define a rule so we can track line numbers
        def t_newline(t):
            r'\n+'
            t.lexer.lineno += len(t.value)

        # A string containing ignored characters (spaces and tabs)
        t_ignore  = '\t '

        # Error handling rule
        def t_error(t):
            print("Illegal character '%s'" % t.value[0])
            t.lexer.skip(1)

        # Build the lexer
        lexer = lex.lex()

        # Test it out
        """data = '''
        SecRule TX:PARANOIA_LEVEL "@lt 1" "phase:1,id:920011,nolog,pass,skipAfter:END-REQUEST-920-PROTOCOL-ENFORCEMENT"
        SecRule TX:OUTBOUND_ANOMALY_SCORE "@ge %{tx.outbound_anomaly_score_threshold}" \
    	"phase:logging,\
    	id:980140,\
    	t:none,\
    	log,noauditlog,\
    	pass,\
            tag:'event-correlation',\
    	msg:'Outbound Anomaly Score Exceeded (score %{TX.OUTBOUND_ANOMALY_SCORE}): %{tx.msg}'"
        '''"""

        # Give the lexer some input
        lexer.input(data)

        # Tokenize
        while True:
            tok = lexer.token()
            if not tok:
                break      # No more input
            print(tok)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse ModSecurity Rules')
    parser.add_argument('--file', dest='rulefile', required=True,
                    help='the file containing a list of ModSecurity rules to \
                    parse')

    args = parser.parse_args()
    data = ""       # variable to hold string of the contents of the rule file

    with open(args.rulefile, 'r') as f:
        #import pdb; pdb.set_trace()
        # for every line in the file, check to see if it is blank or
        # check if it does not statt with SecRule
        for line in f:
            first_char_index = len(line) - len(line.lstrip())
            # if the line is empty or starts with a #, don't parse it
            if len(line) == 1:
                next
            # if the line has whitespace chars but is empty (ex. \t\t\n)
            elif len(line.lstrip()) == 0:
                next
            # if the line starts with a comment, skip
            elif line[first_char_index] == '#':
                #print('comment line', end='')
                next
            # if the line does not match any of the previous criteria, it is a
            # valid rule line
            elif line.rstrip()[-1:] == '\\':
                #print("ENDS WITH BACKSLASH")
                data += line.lstrip().rstrip()[:-1]
            else:
                #print(line.lstrip().rstrip()[:-1])
                data += line
            #print line
        #data = f.read()
    #print(data, end='')
    # data is a string of one or more rules
    p = Parser(data)
    p.parse()
