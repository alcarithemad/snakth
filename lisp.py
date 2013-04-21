import ast
from lexer import Lexer
from parser import Parser

if __name__ == '__main__':
    from pprint import pprint
    import sys
    #ex = '(raw_input (str (** (~ (and 2 3)) (int "101" (+ 1 1)))))'
    ex = file(sys.argv[1], 'rb').read()
    # ex = '(if False (print))'
    # ex = '(print (> 3 2))'
    l = Lexer(ex)
    while 1:
        x = l.token()
        pprint(x)
        if x == l.EOF:
            break
    l = Lexer(ex)
    p = Parser(l)
    print ast.dump(p.run())
    exec compile(p.tree, '<string>', 'exec')