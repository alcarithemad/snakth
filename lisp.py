import ast
import string

'''
(if (> a b)
  (x 1 (+ y 2))
  False
)
'''
class Lexer(object):
    IDENTIFIER = list(string.letters+string.punctuation+string.digits)
    IDENTIFIER.remove('"')
    IDENTIFIER.remove('(')
    IDENTIFIER.remove(')')
    START_IDENT = list(string.letters+string.punctuation)
    START_IDENT.remove('"')
    ESCAPED_CHARS = '"\\'
    EOF = ('EOF', '')

    def __init__(self, code):
        self.input = code
        self.start = 0
        self.pos = -1
        self.depth = 0
        self.tokens = []
        self.state = self.state_start

    def emit(self, typ, val):
        self.tokens.append((typ, val))

    def next(self):
        self.pos += 1
        if self.pos < len(self.input):
            return self.input[self.pos]
        else:
            raise EOFError

    def unread(self):
        self.pos -= 1

    def accept(self, valid):
        out = ''
        try:
            while self.peek() in valid:
                out += self.next()
        except EOFError:
            if len(out):
                return out
            else:
                raise
        return out

    def peek(self):
        if self.pos+1 < len(self.input):
            return self.input[max(self.pos+1, 0)]
        else:
            raise EOFError

    def token(self):
        while 1:
            if len(self.tokens):
                return self.tokens.pop(0)
            else:
                try:
                    self.state = self.state()
                except EOFError:
                    return self.EOF

    def state_start(self):
        c = self.peek()
        # print 'c', c
        if c == '(':
            return self.state_call
        elif c == ')':
            return self.state_endcall
        elif c in string.whitespace:
            return self.state_chomp
        elif c == ';':
            return self.state_comment
        elif c == '"':
            return self.state_string
        elif c in string.digits:
            return self.state_number
        elif c in self.START_IDENT:
            return self.state_token

    def state_call(self):
        self.next() # swallow the paren that got us here
        self.depth += 1
        # print 'calling', self.peek()
        self.state = self.state_start
        c = []
        t = self.token()
        while t[0] != 'commit':
            c.append(t)
            t = self.token()
            if t[0] == self.EOF:
                raise EOFError
        #print 'tok', t
        self.emit('call', c)
        return self.state_start

    def state_endcall(self):
        self.next()
        self.depth -= 1
        if self.depth < 0:
            raise SyntaxError('mismatched parens')
        self.emit('commit', '')
        return self.state_start

    def state_string(self):
        self.next() # swallow the opening "
        s = self.next()
        c = self.peek()
        escaped = c in self.ESCAPED_CHARS
        while c:
            if escaped and c in self.ESCAPED_CHARS:
                escaped = False
                s += self.next()
            elif escaped and c not in self.ESCAPED_CHARS:
                raise ValueError('bad escape sequence', s+self.peek())
            elif c == '\\':
                escaped = True
                self.next()
            elif c == '"' and escaped:
                s += self.next()
            elif c == '"' and not escaped:
                break
            else:
                s += self.next()
            c = self.peek()
        self.next() # swallow the closing "
        self.emit(str, s)
        return self.state_start

    def state_comment(self):
        while self.peek() != '\n':
            self.next()
        return self.state_start

    def state_chomp(self):
        while self.peek() in string.whitespace:
            self.next()
        return self.state_start

    def state_token(self):
        s = self.next()
        s += self.accept(self.IDENTIFIER)
        self.emit('name', s)
        return self.state_start

    def state_number(self):
        n = self.accept(string.digits)
        self.emit(int, n)
        return self.state_start

class Parser(object):
    PSEUDONAMES = ['+']
    BINOPS = {
        '+':ast.Add,
        '-':ast.Sub,
        '*':ast.Mult,
        '/':ast.Div,
        '%':ast.Mod,
        '**':ast.Pow,
        '<<':ast.LShift,
        '>>':ast.RShift,
        '|':ast.BitOr,
        '^':ast.BitXor,
        '&':ast.BitAnd,
        '//':ast.FloorDiv
    }
    UNARYOPS = {
        '+':ast.UAdd,
        '-':ast.USub,
        'not':ast.Not,
        '~':ast.Invert,
    }
    BOOLOPS = {
        'and':ast.And,
        'or':ast.Or,
    }

    def __init__(self, lexer):
        self.lexer = lexer
        self.tree = ast.Module([])
        self.tokens = []
        self.scopes = [ast.Load()]

    def token(self):
        if len(self.tokens):
            return self.tokens.pop(0)
        else:
            return self.lexer.token()

    def unread(self, tok):
        self.tokens.insert(0, tok)

    def parse_name(self, tok):
        return ast.Name(tok[1], self.scopes[-1])
        
    def parse_int(self, tok):
        return ast.Num(int(tok[1]))

    def parse_str(self, tok):
        return ast.Str(tok[1])

    def parse_call(self, tok, expr=True):
        call = tok[1]
        c_ast = ast.Call(keywords=[])
        if call[0][0] == 'call':
            c = self.parse_call(call[0])
        elif call[0][0] == 'name':
            name = call[0][1]
            if name in self.BINOPS and len(call) == 3:
                op = ast.BinOp(
                    left=self.parse(call[1], expr=False),
                    op=self.BINOPS[name](),
                    right=self.parse(call[2], expr=False),
                )
                if expr:
                    return ast.Expr(op)
                else:
                    return op
            elif name in self.BINOPS and len(call) > 3:
                pass # TODO: handle (+ 1 2 3)
            elif name in self.BOOLOPS:
                values = [self.parse(v, expr=False) for v in call[1:]]
                op = ast.BoolOp(
                    op=self.BOOLOPS[name](),
                    values=values
                )
                if expr:
                    return ast.Expr(op)
                else:
                    return op
            elif name in self.UNARYOPS:
                assert len(call) == 2
                op = ast.UnaryOp(
                    op=self.UNARYOPS[name](),
                    operand=self.parse(call[1], expr=False)
                )
                if expr:
                    return ast.Expr(op)
                else:
                    return op
            else:
                func = self.parse_name(call[0])
            c_ast.func = func
        args = []
        for t in call[1:]:
            if t[0] == 'call':
                v = self.parse(t).value
            else:
                v = self.parse(t)
            args.append(v)
        c_ast.args = args
        if expr:
            return ast.Expr(c_ast)
        else:
            return c_ast


    def parse(self, tok=None, expr=True):
        t = tok or self.token()
        if t[0] == 'call':
            return self.parse_call(t, expr=expr)
        elif t[0] == 'name':
            return self.parse_name(t)
        elif t[0] == int:
            return self.parse_int(t)
        elif t[0] == str:
            return self.parse_str(t)

    def run(self):
        t = self.token()
        while t != self.lexer.EOF:
            self.tree.body.append(self.parse(t))
            t = self.token()
        ast.fix_missing_locations(self.tree)
        return self.tree

if __name__ == '__main__':
    from pprint import pprint
#     ex = '(+ 1 (- 2 s3! "asdf $%#%$ escaped \\" works!")); asdf'
#     ex = '''
# (raw_input (str "test"))
# ;(if (> a b);test
# ;  (x 1 (+ y 2))
# ;  False
# ;)
# ;(
# ;  (lambda x (* x x)) 3
# ;)
# '''
    #ex = '(raw_input (str (** (~ (and 2 3)) (int "101" (+ 1 1)))))'
    ex = '(raw_input (str (and True True False)))'
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