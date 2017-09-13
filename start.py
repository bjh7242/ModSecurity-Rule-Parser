#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ply.yacc as yacc
import ply.lex as lex

def main():
    # List of token names.   This is always required
    tokens = (
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
    t_ignore  = '\t'

    # Error handling rule
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Build the lexer
    lexer = lex.lex()

    # Test it out
    data = '''
    SecRule TX:PARANOIA_LEVEL "@lt 1" "phase:1,id:920011,nolog,pass,skipAfter:END-REQUEST-920-PROTOCOL-ENFORCEMENT"
    '''

    # Give the lexer some input
    lexer.input(data)

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break      # No more input
        print(tok)



if __name__ == "__main__":
    main()
