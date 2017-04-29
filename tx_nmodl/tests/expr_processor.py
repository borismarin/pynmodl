from textx.metamodel import metamodel_from_str
from textx.model import parent_of_type


class ModExpr2Lems(object):
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

    def t(self, type_str):
        return self.mm.namespaces[None][type_str]

    def is_txtype(self, obj, type_str):
        return isinstance(obj, self.t(type_str))

    def binop(self, node):
        ops = [n.lems for n in node.op[1:]]
        l = node.op[0].lems
        node.lems = l + ''.join(ops)

    def addition(self, add):
        self.binop(add)

    def multiplication(self, mul):
        self.binop(mul)

    def exponentiation(self, exp):
        self.binop(exp)

    def negation(self, neg):
        s = neg.sign.lems if neg.sign else ''
        v = neg.primary.lems
        neg.lems = s + v

    def paren(self, par):
        p = par.ex
        par.lems = '(' + p + ')'

    def num(self, num):
        num.lems = num.num

    def varref(self, var):
        ivar = var.var
        if(self.is_txtype(ivar, 'FuncPar')):
            lems = '{{{}}}'.format(ivar.name)
        elif(self.is_txtype(ivar, 'FuncDef')):
            parnames = [p.name for p in ivar.pars]
            lems = '{}_{{{}}}_{{{}}}'.format(ivar.name, *parnames)
        elif(self.is_txtype(ivar, 'Local')):
            parent = parent_of_type('FuncDef', ivar)
            parnames = [p.name for p in parent.pars]
            lems = '{}_{{{}}}_{{{}}}__{}'.format(
                parent.name, *parnames, ivar.name)
        else:
            lems = ivar.name
        var.lems = lems

    def op(self, op):
        op.lems = ' ' + op.o + ' '

    def pm(self, pm):
        self.op(pm)

    def md(self, md):
        self.op(md)

    def exp(self, exp):
        self.op(exp)

    def funccall(self, f):
        args = [a.lems for a in f.args]
        arg_val = dict(zip([p.name for p in f.func.pars], args))
        f.deps = f.func.template.format(**arg_val)
        f.lems = '{}_{}'.format(f.func.name, '_'.join(args))

    def assign(self, asgn):
        var = asgn.variable
        exp = asgn.expression
        if var:
            asgn.lems = self.func_deps(
                exp) + '<DerivedVariable name="{}" value="{}/>"'.format(var.lems, exp.lems)
        else:
            asgn.lems = exp.lems

    def ifstmt(self, ifs):
        iff = 'else\n' + ifs.false_blk.lems if ifs.false_blk else ''
        ift = ifs.true_blk.lems if ifs.true_blk else ''
        cond = ifs.cond.lems
        ifs.lems = '<CondDerVar>\n\t<Case cond="{}">\n<Case{}'.format(
            cond, ift, iff)

    def block(self, b):
        s = [s.lems for s in b.stmts]
        b.lems = '{' + '\n'.join(s) + '}'

    def funcdef(self, f):
        stmts = [s.lems for s in f.stmts]
        args = [p.lems for p in f.pars]
        f.lems = 'FUNCTION {}({}){{\n\t{}\n}}'.format(f.name, args, stmts)
        f.template = self.func_template(f, stmts, args)

    def func_template(self, f, stmts, args):
        from itertools import compress
        is_asgn = map(lambda el: self.is_txtype(el, 'Assignment'), f.stmts)
        asgns = [s for s in compress(stmts, is_asgn)]
        return '\n'.join(asgns)

    def func_deps(self, node):
        from textx.model import children_of_type
        fcalls = children_of_type('FuncCall', node)
        return '\n'.join([fc.deps for fc in fcalls] + [''])

    def locals(self, loc):
        loc.lems = ''
        #locs = ', '.join([l.lems for l in loc.vars])
        #loc.lems = 'LOCAL {}'.format(locs)

    def local(self, loc):
        parent = parent_of_type('FuncDef', loc)
        parnames = [p.name for p in parent.pars]
        locname = '{}_{{{}}}_{{{}}}__{}'.format(
            parent.name, *parnames, loc.name)
        loc.lems = locname

    def funcpar(self, fp):
        fp.lems = fp.name

    def relational(self, l):
        self.binop(l)

    def logicalcon(self, l):
        self.binop(l)

    def logcon(self, l):
        self.op(l)

    def relop(self, r):
        self.op(r)

    def primed(self, p):
        var = p.variable
        expression = p.expression
        lems = self.func_deps(expression) +\
            '<TimeDerivative variable="{}" value="{}"/>'.format(
                var, expression.lems)
        p.lems = lems

    def gen_nml(self, mod):
        self.stack2 = []
        m = self.mm.model_from_str(mod)
        s = 72 * '-' + '\n' + '\n'.join([s.lems for s in m.stmts])
        return s


def main(debug=False):
    c = ModExpr2Lems()
    #print(c.gen_nml("G x x'=-x+1"))
    print(c.gen_nml(
        "G V  FUNCTION f(x,y){LOCAL a a=2*x f=a+y} x' = 1 + f(3,V) y'=2+f(4,V)"))

    #print(c.gen("G V  FUNCTION f(x,y){LOCAL a a=2*x if(V>10){f=a+y}else{f=y}} x' = 1 + f(3,V) y'=2+f(4,V)"))


if __name__ == '__main__':
    main()
