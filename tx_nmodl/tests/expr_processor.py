from textx.metamodel import metamodel_from_str
from textx.model import parent_of_type


class NoTypes(object):
    def __init__(self):
        self.mm = metamodel_from_str('''
            Prog: globals*=Global funcDefs*=FuncDef stmts*=Statement;
            
            NUMBER: /[-+]?[0-9]*\.?[0-9]*([eE][-+]?[0-9]+)?/;
            Statement: Block | Primed | Assignment | IfStatement | WhileStatement | Expression;
            Block: '{' stmts*=Statement '}';


            IfStatement: 'if' '(' cond=Expression ')'
                            true_blk=Block ('else' false_blk=Block)?;
            WhileStatement: 'while' '(' cond=Expression ')' Block;
            
            Primed: variable=cID+"'" '='!'='? expression=LogicalCon;

            Expression: Assignment;
            Assignment: (variable=VarRef '='!'=')? expression=LogicalCon;
            LogicalCon: op=Relational (op=LogCon op=Relational)*;
            Relational: op=Addition (op=RelOp op=Addition)*;
            Addition: op=Multiplication (op=PlusOrMinus op=Multiplication)* ;
            Multiplication: op=Exponentiation (op=MulOrDiv op=Exponentiation)*;
            Exponentiation: op=Negation (op=Exp op=Exponentiation)?; //using Exponentiation? here for right assoc
            Negation: (sign=PlusOrMinus)?  primary=Primary;
            Primary: FuncCall | Paren | Num | VarRef ;
            
            
            Var: Local | Global | FuncPar | FuncDef;
            VarRef: var=[Var|cID];
            Num: num=NUMBER;
            FuncCall: func=[FuncDef|cID]'(' args*=Expression[',']  ')';
            Paren: ('(' ex=Expression ')');
           
            Global: 'G' name=cID;
            Local: name=cID;
            Locals: 'LOCAL' vars*=Local[','];
            Unit: '(' cID ')';
            FuncPar: name=cID (unit=Unit)?; 
            FuncStmt: Locals | Statement;
            FuncDef:  'FUNCTION' name=cID '(' pars*=FuncPar[','] ')' (unit=Unit)? 
                        '{' stmts*=FuncStmt '}';
            
            PlusOrMinus: o=/\+|\-/;
            MulOrDiv: o=/\*|\//;
            Exp: o='^';
            RelOp: o=/([<>]=?|[!=]=)/;
            LogCon: o=/(&&)|(\|\|)/;
            
            Keyword: 'if' | 'else' | 'while' | 'FUNCTION' | 'LOCAL' | 'G';
            cID: !Keyword ID; 

            ''')
        self.mm.register_obj_processors({
            'Addition': self.addition,
            'Multiplication': self.multiplication,
            'Exponentiation': self.exponentiation,
            'Negation': self.negation,
            'Paren': self.paren,
            'FuncCall': self.funccall,
            'Num': self.num,
            'VarRef': self.varref,
            'PlusOrMinus': self.pm,
            'MulOrDiv': self.md,
            'Exp': self.exp,
            'Assignment': self.assign,
            'IfStatement': self.ifstmt,
            'Relational': self.relational,
            'LogicalCon': self.logicalcon,
            'Block': self.block,
            'RelOp': self.relop,
            'LogCon': self.logcon,
            'FuncDef': self.funcdef,
            'Locals': self.locals,
            'FuncPar': self.funcpar,
            'Primed': self.primed,
            'Local': self.local,
        })
        self.stack = []
        self.stack2 = []
        self.zzz = []

    def t(self, type_str):
        return self.mm.namespaces[None][type_str]

    def is_txtype(self, obj, type_str):
        return isinstance(obj, self.t(type_str))

    def binop(self, node):
        ops = self.unpack_stack(node.op[1:])
        l = self.stack.pop()
        self.stack.append(l + ''.join(ops))

        ops = self.unpack_stack2(node.op[1:])
        l = self.stack2.pop()
        self.stack2.append(l + ''.join(ops))

    def addition(self, add):
        self.binop(add)

    def multiplication(self, mul):
        self.binop(mul)

    def exponentiation(self, exp):
        self.binop(exp)

    def negation(self, neg):
        s = self.stack.pop() if neg.sign else ''
        v = self.stack.pop()
        self.stack.append(v + s)

        s = self.stack2.pop() if neg.sign else ''
        v = self.stack2.pop()
        self.stack2.append(v + s)

    def paren(self, par):
        p = self.stack.pop()
        self.stack.append('(' + p + ')')
        self.stack2.append('(' + p + ')')

    def num(self, num):
        # self.stack.append('{:g}'.format(num.num))
        self.stack.append(num.num)
        self.stack2.append(num.num)

    def varref(self, var):
        self.stack.append(var.var.name)
        if(self.is_txtype(var.var, 'FuncPar')):
            self.stack2.append('{{{}}}'.format(var.var.name))
        elif(self.is_txtype(var.var, 'FuncDef')):
            parnames = [p.name for p in var.var.pars]
            self.stack2.append(
                '{}_{{{}}}_{{{}}}'.format(var.var.name, *parnames))
        else:
            self.stack2.append(var.var.name)

    def op(self, op):
        self.stack.append(' ' + op.o + ' ')
        self.stack2.append(' ' + op.o + ' ')

    def pm(self, pm):
        self.op(pm)

    def md(self, md):
        self.op(md)

    def exp(self, exp):
        self.op(exp)

    def funccall(self, f):
        fargs = self.unpack_stack(f.args)
        self.stack.append('{}({})'.format(f.func.name, ', '.join(fargs)))

        args = self.unpack_stack2(f.args)
        arg_val = dict(zip([p.name for p in f.func.pars], args))
        self.zzz.append(f.func.template.format(**arg_val))
        self.stack2.append('{}_{}'.format(f.func.name, '_'.join(args)))

    def assign(self, asgn):
        if asgn.variable:
            r = self.stack.pop()
            l = self.stack.pop()
            self.stack.append('{} = {}'.format(l, r))

            r = self.stack2.pop()
            l = self.stack2.pop()
            self.stack2.append(
                '<DerivedVariable name="{}" value="{}/>"'.format(l, r))
        else:
            exp = self.stack.pop()
            self.stack.append(exp)

            exp = self.stack2.pop()
            self.stack2.append(exp)

    def ifstmt(self, ifs):
        iff = 'else\n' + self.stack.pop() if ifs.false_blk else ''
        ift = self.stack.pop() if ifs.true_blk else ''
        cond = self.stack.pop()
        self.stack.append('if({})\n{}\n{}'.format(cond, ift, iff))

        iff = 'else\n' + self.stack2.pop() if ifs.false_blk else ''
        ift = self.stack2.pop() if ifs.true_blk else ''
        self.stack2.append(
            '<CondDerVar>\n\t<Case cond="{}">\n<Case{}'.format(cond, ift, iff))

    def block(self, b):
        s = self.unpack_stack(b.stmts)
        self.stack.append('{' + '\n'.join(s) + '}')
        s = self.unpack_stack2(b.stmts)
        self.stack2.append('{' + '\n'.join(s) + '}')

    def relational(self, l):
        self.binop(l)

    def logicalcon(self, l):
        self.binop(l)

    def logcon(self, l):
        self.op(l)

    def funcdef(self, f):
        stmts = '\n\t'.join(self.unpack_stack(f.stmts))
        args = ', '.join(self.unpack_stack(f.pars))
        self.stack.append(
            'FUNCTION {}({}){{\n\t{}\n}}'.format(f.name, args, stmts))

        stmts = self.unpack_stack2(f.stmts)
        args = self.unpack_stack2(f.pars)
        self.stack2.append(
            'FUNCTION {}({}){{\n\t{}\n}}'.format(f.name, args, stmts))
        f.template = self.func_template(f, stmts, args)

    def func_template(self, f, stmts, args):
        from itertools import compress
        is_asgn = map(lambda el: self.is_txtype(el, 'Assignment'), f.stmts)
        asgns = [s for s in compress(stmts, is_asgn)]
        return '\n'.join(asgns)

    def locals(self, l):
        locs = ', '.join(self.unpack_stack(l.vars))
        self.stack.append('LOCAL {}'.format(locs))

        locs = ', '.join(self.unpack_stack2(l.vars))
        self.stack2.append('LOCAL {}'.format(locs))

    def local(self, l):
        parent = parent_of_type('FuncDef', l)
        parnames = [p.name for p in parent.pars]
        l.name = '{}_{{{}}}_{{{}}}__{}'.format(parent.name, *parnames, l.name)
        self.stack.append(l.name)
        self.stack2.append(l.name)

    def funcpar(self, fp):
        self.stack.append(fp.name)
        self.stack2.append(fp.name)

    def relop(self, r):
        self.op(r)

    def primed(self, p):
        expression = self.stack.pop()
        #var = self.stack.pop()
        var = p.variable
        self.stack.append('d{}/dt = {}'.format(var, expression))

        expression = self.stack2.pop()
        #var = self.stack2.pop()
        var = p.variable
        self.zzz.append(
            '<TimeDerivative variable="{}" value="{}"/>'.format(var, expression))

    def unpack_stack(self, node):
        return list(reversed([self.stack.pop() for _ in node]))

    def unpack_stack2(self, node):
        return list(reversed([self.stack2.pop() for _ in node]))

    def gen(self, mod):
        self.stack = []
        self.mm.model_from_str(mod)
        s = 72 * '-' + '\n' + '\n'.join(self.stack)
        self.stack = []
        return s

    def gen_nml(self, mod):
        self.stack2 = []
        self.mm.model_from_str(mod)
        s = 72 * '-' + '\n' + '\n'.join(self.stack2)
        self.stack2 = []
        return '\n'.join(self.zzz)


def main(debug=False):
    c = NoTypes()
    #print(c.gen('G a G b a=1+1'))
    #print(c.gen('1 + 1 + 2 / 3'))
    #print(c.gen('1e12 + (3*a + 2)'))
    #print(c.gen('1e12 * (a + 2/3)'))
    # print(c.gen('2^3^4'))
    #print(c.gen('if(1 > 2){a = 3 + 3 b=4 }'))
    #print(c.gen('if(1+1){a=2} else {3 + 4 }'))
    #print(c.gen('if(a==1 && 2 < 3 ){} else {4 + 5 }'))
    #print(c.gen('G slow_invl G burst if(slow_invl == 0 || burst != 0.0 ){}'))
    #print(c.gen('G slow_invl G burst G burst_len if(slow_invl == 0 || (burst != 0. && burst_len > 1)){}'))
    #print(c.gen('FUNCTION f(x,y){LOCAL a a=2*x f=a+y}'))
    #print(c.gen('FUNCTION f(x,y){LOCAL a f=a*x^y} f(1,f(2,3))'))
    #print(c.gen('FUNCTION f(x,y){LOCAL a f=a*x^y} f(1,f(2,3))'))

    #print(c.gen("G x x'=-x+1"))
    # print(c.gen("x'=-x+1"))
    #print(c.gen_nml("G x x'=-x+1"))
    print(c.gen_nml(
        "G V  FUNCTION f(x,y){LOCAL a a=2*x f=a+y} x' = 1 + f(3,V) y'=2+f(4,V)"))

    #print(c.gen("G V  FUNCTION f(x,y){LOCAL a a=2*x if(V>10){f=a+y}else{f=y}} x' = 1 + f(3,V) y'=2+f(4,V)"))


if __name__ == '__main__':
    main()
