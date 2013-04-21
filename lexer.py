import string

class Lexer(object):
    IDENTIFIER = list(string.letters+string.punctuation+string.digits)
    IDENTIFIER.remove('"')
    IDENTIFIER.remove('(')
    IDENTIFIER.remove(')')
    IDENTIFIER.remove(':')
    IDENTIFIER.remove('[')
    START_IDENT = list(string.letters+string.punctuation)
    START_IDENT.remove('"')
    START_IDENT.remove(':')
    START_IDENT.remove('[')
    ESCAPED_CHARS = '"\\'
    NUMBERS = string.digits+'+-'
    EOF = ['EOF', '']

    def __init__(self, code):
        self.input = code
        self.start = 0
        self.pos = -1
        self.depth = 0
        self.tokens = []
        self.state = self.state_start

    def emit(self, typ, val):
        self.tokens.append([typ, val])

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
        elif c == ':':
            return self.state_vararg
        elif c == '[':
            return self.state_subscript
        elif c == ']':
            return self.state_endsub
        elif c in self.NUMBERS:
            return self.state_number
        elif c in self.START_IDENT:
            return self.state_token
        raise SyntaxError('invalid state')

    def state_call(self):
        self.next() # swallow the paren that got us here
        self.depth += 1
        self.state = self.state_start
        c = []
        t = self.token()
        c.append(t)
        while 1:
            t = self.token()
            if t[0] == 'attr' and t[1][0][1] == '':
                t[1][0] = c[-1]
                c[-1]= t
                t = False
            elif t[0] == 'subscript':
                t[1][0] = c[-1]
                c[-1]= t
                t = False
                # print c[-1]
            elif t == ['commit', '']:
                break
            elif t == self.EOF:
                raise EOFError
            if t and t[0] != 'commit':
                c.append(t)
            else:
                t = ['', '']
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
        escaped = c == '\\'
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

    def state_subscript(self):
        self.next() # eat a [
        self.state = self.state_start
        s = ['', self.token()]
        while s[-1][1] != 'endsub':
            s.append(['']+list(self.token()))
        self.emit('subscript', s[:-1])
        return self.state_start

    def state_endsub(self):
        self.next()
        self.emit('endsub', '')
        return self.state_start

    def state_token(self):
        s = self.next()
        s += self.accept(self.IDENTIFIER)
        if self.peek() == ':':
            self.next()
            self.state = self.state_start
            expr = self.token()
            # print 'expr', expr
            self.emit('kwname', (s, expr))
        elif '.' in s:
            attrs = s.split('.')
            name = attrs[0]
            attrs = attrs[1:]
            # print ('attr', (name, attrs))
            self.emit('attr', [['name', name], attrs])
        else:
            self.emit('name', s)
        return self.state_start

    def state_vararg(self):
        self.next() # swallow the colon that got us here
        self.state = self.state_start
        expr = self.token()
        if expr[0] == 'vararg':
            arg = 'kwarg'
            expr = expr[1]
        else:
            arg = 'vararg'
        # print 'expr', expr
        self.emit(arg, expr)
        return self.state_start

    def state_number(self):
        n = self.accept(self.NUMBERS)
        self.emit(int, n)
        return self.state_start