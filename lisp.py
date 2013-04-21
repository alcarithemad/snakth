import ast
from lexer import Lexer
from parser import Parser

if __name__ == '__main__':
    from pprint import pprint
    import sys
    ex = file(sys.argv[1], 'rb').read()
    # l = Lexer(ex)
    # while 1:
    #     x = l.token()
    #     # pprint(x)
    #     if x == l.EOF:
    #         break
    l = Lexer(ex)
    p = Parser(l)
    p.run()
    # print ast.dump(p.tree)
    exec compile(p.tree, sys.argv[1], 'exec')