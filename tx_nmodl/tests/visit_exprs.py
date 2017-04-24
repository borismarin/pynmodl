from textx.metamodel import metamodel_from_str


class NoTypes(object):
    def __init__(self):
        self.mm = metamodel_from_str('''
            Prog: stmts*=Statement;

            NUMBER: /[-+]?[0-9]*\.?[0-9]*([eE][-+]?[0-9]+)?/;
            Statement: Block | Assignment | IfStatement | WhileStatement | Expression | FuncDef;
            Block: '{' stmts*=Statement '}';


            IfStatement: 'if' '(' cond=Expression ')'
                            true_blk=Block ('else' false_blk=Block)?;
            WhileStatement: 'while' '(' cond=Expression ')' Block;

            Expression: Assignment;
            Assignment: (variable=Var '='!'=')? expression=LogicalCon;
            LogicalCon: op=Relational (op=LogCon op=Relational)*;
            Relational: op=Addition (op=RelOp op=Addition)*;
            Addition: op=Multiplication (op=PlusOrMinus op=Multiplication)* ;
            Multiplication: op=Exponentiation (op=MulOrDiv op=Exponentiation)*;
            Exponentiation: op=Negation (op=Exp op=Exponentiation)?; //using Exponentiation? here for right assoc
            Negation: (sign=PlusOrMinus)?  primary=Primary;
            Primary: FuncCall | Paren | Num | Var ;
            Var:var=cID;
            Num: num=NUMBER;
            FuncCall: func=cID'(' args*=Expression[',']  ')';
            Paren: ('(' ex=Expression ')');

            Local: 'LOCAL' vars*=Var[','];
            Unit: '(' cID ')';
            FuncPar: name=cID (unit=Unit)?; 
            FuncDef:  'FUNCTION' name=cID '(' pars*=FuncPar[','] ')' (unit=Unit)? 
                        '{' (locals=Local | stmts=Statement)* '}';

            PlusOrMinus: o=/\+|\-/;
            MulOrDiv: o=/\*|\//;
            Exp: o='^';
            RelOp: o=/([<>]=?|[!=]=)/;
            LogCon: o=/(&&)|(\|\|)/;

            Keyword: 'if' | 'else' | 'while' | 'FUNCTION' | 'LOCAL';
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
            'Var': self.var,
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
            'Local': self.local,
            'FuncPar': self.funcpar,
        })
        self.stack = []

    def binop(self, node):
        ops = reversed([self.stack.pop() for _ in node.op[1:]])
        self.stack.append(self.stack.pop() + ''.join(ops))

    def addition(self, add):
        self.binop(add)

    def multiplication(self, mul):
        self.binop(mul)

    def exponentiation(self, exp):
        ops = reversed([self.stack.pop() for _ in exp.op[1:]])
        self.stack.append(self.stack.pop() + ''.join(ops))

    def negation(self, neg):
        s = self.stack.pop() if neg.sign else ''
        self.stack.append(self.stack.pop() + s)

    def paren(self, par):
        self.stack.append('(' + self.stack.pop() + ')')

    def num(self, num):
        # self.stack.append('{:g}'.format(num.num))
        self.stack.append(num.num)

    def var(self, var):
        self.stack.append(var.var)

    def op(self, op):
        self.stack.append(' ' + op.o + ' ')

    def pm(self, pm):
        self.op(pm)

    def md(self, md):
        self.op(md)

    def exp(self, exp):
        self.op(exp)

    def funccall(self, f):
        args = ',  '.join(reversed([self.stack.pop() for _ in f.args]))
        self.stack.append('{}({})'.format(f.func, args))

    def assign(self, asgn):
        if asgn.variable:
            r = self.stack.pop()
            l = self.stack.pop()
            self.stack.append('{} = {}'.format(l, r))
        else:
            self.stack.append(self.stack.pop())

    def ifstmt(self, ifs):
        iff = 'else' + self.stack.pop() if ifs.false_blk else ''
        ift = self.stack.pop() if ifs.true_blk else ''
        cond = self.stack.pop()
        self.stack.append('if({}){}{}'.format(cond, ift, iff))

    def block(self, b):
        s = [self.stack.pop() for _ in b.stmts]
        self.stack.append('{' + '\n'.join(s) + '}')

    def relational(self, l):
        self.binop(l)

    def logicalcon(self, l):
        self.binop(l)

    def logcon(self, l):
        self.op(l)

    def funcdef(self, f):
        args = ',  '.join(reversed([self.stack.pop() for _ in f.pars]))
        locs = self.stack.pop() if f.locals else ''
        self.stack.append(
            'FUNCTION {}{{\n\t{}\n\t{}\n}}'.format(f.name, locs, args))

    def local(self, l):
        locs = ',  '.join(reversed([self.stack.pop() for _ in l.vars]))
        self.stack.append('LOCAL {}'.format(locs))

    def funcpar(self, fp):
        self.stack.append(fp.name)

    def relop(self, r):
        self.op(r)

    def gen(self, mod):
        self.mm.model_from_str(mod)
        return self.stack.pop()


def main(debug=False):
    c = NoTypes()
    print(c.gen('a=1+1'))
    print(c.gen('1 + 1 + 2 / 3'))
    print(c.gen('1e12 + (3*a + 2)'))
    print(c.gen('1e12 * (a + 2/3)'))
    print(c.gen('atan2(a * 2, 1-(b+3) - cos(cd^3)/4+5^6)'))
    print(c.gen('2^3^4'))
    print(c.gen('if(1 > 2){a = 3 + 3 b=4 }'))
    print(c.gen('if(1+1){a=2} else {3 + 4 }'))
    print(c.gen('if(a==1 && 2 < 3 ){} else {4 + 5 }'))
    print(c.gen('if(slow_invl == 0 || burst != 0.0 ){}'))
    print(c.gen('if(slow_invl == 0 || (burst != 0. && burst_len > 1)){}'))
    print(c.gen('FUNCTION f(x){LOCAL a f=a*x}'))

if __name__ == '__main__':
    main()
