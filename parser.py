import ast

class Parser(object):
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
    CMPOPS = {
        '=':ast.Eq,
        '!=':ast.NotEq,
        '<':ast.Lt,
        '<=':ast.LtE,
        '>':ast.Gt,
        '>=':ast.GtE,
        'is':ast.Is,
        "isn't":ast.IsNot,
        'in':ast.In,
        'not-in':ast.NotIn,
    }

    def __init__(self, lexer):
        self.lexer = lexer
        self.tree = ast.Module([])
        self.tokens = []

    def token(self):
        if len(self.tokens):
            return self.tokens.pop(0)
        else:
            return self.lexer.token()

    def unread(self, tok):
        self.tokens.insert(0, tok)

    def parse_name(self, tok, ctx=ast.Load()):
        return ast.Name(tok[1], ctx)
        
    def parse_int(self, tok):
        return ast.Num(int(tok[1]))

    def parse_str(self, tok):
        return ast.Str(tok[1])

    def parse_call(self, tok, expr=True):
        call = tok[1]
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
            elif name in self.CMPOPS:
                op = ast.Compare(
                    left = self.parse(call[1], expr=False),
                    ops=[self.CMPOPS[name]()],
                    comparators=[self.parse(call[2], expr=False)]
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
            elif name == 'print':
                # TODO: replace me with the print_function from future
                values = [self.parse(v, expr=False) for v in call[1:] if v[0] != 'kwname']
                kwargs = dict((v[1][0], self.parse(v[1][1], expr=False)) for v in call[1:] if v[0] == 'kwname')
                if 'nl' in kwargs:
                    if kwargs['nl'].id == 'True':
                        nl = True
                    elif kwargs['nl'].id == 'False':
                        nl = False
                    else:
                        raise SyntaxError('invalid option "nl" passed to print')
                else:
                    nl = True
                stmt = ast.Print(
                    values=values,
                    nl=nl,
                )
                return stmt
            elif name == 'if':
                test = self.parse(call[1], expr=False)
                body = [self.parse(call[2], expr=False)]
                print len(call)
                if len(call) == 4:
                    orelse = [self.parse(call[3], expr=False)]
                else:
                    orelse = []
                stmt = ast.If(
                    test=test,
                    body=body,
                    orelse=orelse,    
                )
                return stmt
            elif name == 'def':
                f_name = call[1][1]
                args = [(i, self.parse(v, expr=False)) for i, v in enumerate(call[2][1]) if v[0] != 'kwname']
                args += [(i, self.parse(('name', v[1][0]), expr=False), self.parse(v[1][1], expr=False)) for i, v in enumerate(call[2][1]) if v[0] == 'kwname']
                args.sort()
                vararg = None
                kwarg = None
                args = [a[1:] for a in args]
                defaults = []
                print args
                for argument in args:
                    arg = argument[0]
                    if len(argument) > 1:
                        defaults.append(argument[1])
                    arg.ctx = ast.Param()
                    if arg.id.startswith('**'):
                        kwarg = arg
                    elif arg.id.startswith('*'):
                        vararg = arg
                args = [a[0] for a in args]
                try:
                    args.remove(vararg)
                    vararg = vararg.id.lstrip('*')
                except ValueError: pass
                try:
                    args.remove(kwarg)
                    kwarg = kwarg.id.lstrip('**')
                except ValueError: pass
                args = ast.arguments(args, vararg, kwarg, defaults)
                print ast.dump(args)
                print 'body', call[3:]
                func = ast.FunctionDef(
                    name=f_name,
                    args=args,
                    body=[self.parse(v) for v in call[3:]],
                    decorator_list=[], # not sure these fit with the syntax
                )
                return func
            elif name == 'return':
                if len(call) == 2:
                    op = ast.Return(
                        value=self.parse(call[1], expr=False),
                    )
                else:
                    op = ast.Return()
                return op
            else:
                #this is a regular function call
                # TODO: support calling with varargs
                c_ast = ast.Call()

                func = self.parse_name(call[0])
                c_ast.func = func
                args = [self.parse(v, expr=False) for v in call[1:] if v[0] not in ('vararg', 'kwname', 'kwarg')]
                kwargs = list(ast.keyword(v[1][0], self.parse(v[1][1], expr=False)) for v in call[1:] if v[0] == 'kwname')
                for v in call[1:]:
                    if v[0] == 'vararg':
                        c_ast.starargs = self.parse(v[1], expr=False)
                    elif v[0] == 'kwarg':
                        c_ast.kwargs = self.parse(v[1], expr=False)
                c_ast.args = args
                c_ast.keywords = kwargs
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