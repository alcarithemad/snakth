import ast
import new
import os
import os.path
import sys
import traceback

import __future__

from lexer import Lexer
from parser import Parser

# this import hook is basically cribbed from metapython by Rick Copeland
def install_import_hook():
    if SnakthImporter not in sys.meta_path:
        sys.meta_path.append(SnakthImporter)

class SnakthImporter(object):
    @staticmethod
    def find_module(name, path=None):
        lname = name.rsplit('.', 1)[-1]
        for d in (path or sys.path):
            f = os.path.join(d, lname + '.lisp')
            if os.path.exists(f):
                return SnakthLoader(f)

class SnakthLoader(object):
    def __init__(self, path):
        self.path = path

    def load_module(self, name):
        mod = sys.modules.get(name)
        if not mod:
            mod = load_file(self.path, name)
            if '.' in name:
                parent, child = name.rsplit('.', 1)
                setattr(sys.modules[parent], child, mod)
        return mod

def load_file(fn, name=None):
    if not name:
        name = os.path.splitext(os.path.basename(fn))[0]
    result = new.module(name)
    sys.modules[name] = result
    try:
        code = file(fn, 'rb').read()
        compiled = compile_snakth(code, fn)
        pseudo = {}
        pseudo['__name__'] = name
        exec compiled in pseudo
        sys.modules[name].__dict__.update(pseudo)
        return result
    except:
        del sys.modules[name]
        print traceback.format_exc()
        raise

def compile_snakth(ex, fn='<string>', debug=False):
    # ensure that snakth imports from within snakth files works
    install_import_hook()
    if debug:
        l = Lexer(ex)
        while 1:
            x = l.token()
            pprint(x)
            if x == l.EOF:
                break
    l = Lexer(ex)
    p = Parser(l)
    p.run()
    if debug:
        print ast.dump(p.tree)
    c = compile(p.tree, fn, 'exec', __future__.print_function.compiler_flag)
    return c

if __name__ == '__main__':
    from pprint import pprint
    import argparse
    parser = argparse.ArgumentParser(description='snakth compiler')
    parser.add_argument('-d', '--debug', 
        help='enable compile time debugging (currently just outputs the parse tree)',
        action='store_true'
    )
    parser.add_argument('file', nargs='?')

    args = parser.parse_args()
    if not os.path.exists(args.file or ''):
        parser.print_help()
        sys.exit()

    code = file(args.file, 'rb').read()
    c = compile_snakth(code, args.file, args.debug)
    pseudo = {}
    pseudo['__name__'] = __name__
    exec c in pseudo
