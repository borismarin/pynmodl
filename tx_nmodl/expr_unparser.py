import os
from textx.metamodel import metamodel_from_file

class ExprUnparser(object):
    def __init__(self):
        self.mm = metamodel_from_file(
            os.path.join(os.path.dirname(__file__), 'expressions.tx'))
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
        ops = [n.unparsed for n in node.op[1:]]
        l = node.op[0].unparsed
        node.unparsed = l + ''.join(ops)

    def addition(self, add):
        self.binop(add)

    def multiplication(self, mul):
        self.binop(mul)

    def exponentiation(self, exp):
        self.binop(exp)

    def negation(self, neg):
        s = neg.sign.unparsed if neg.sign else ''
        v = neg.primary.unparsed
        neg.unparsed = s + v

    def paren(self, par):
        p = par.ex.unparsed
        par.unparsed = '(' + p + ')'

    def num(self, num):
        num.unparsed = num.num

    def varref(self, var):
        var.unparsed = var.var.name

    def op(self, op):
        op.unparsed = ' ' + op.o + ' '

    def pm(self, pm):
        self.op(pm)

    def md(self, md):
        self.op(md)

    def exp(self, exp):
        self.op(exp)

    def funccall(self, f):
        args = [a.unparsed for a in f.args]
        f.unparsed = '{}({})'.format(f.func.name, ', '.join(args))

    def assign(self, asgn):
        var = asgn.variable
        exp = asgn.expression
        if var:
            asgn.unparsed = '{} = {}'.format(var.unparsed, exp.unparsed)
        else:
            asgn.unparsed = exp.unparsed

    def ifstmt(self, ifs):
        iff = 'else\n' + ifs.false_blk.unparsed if ifs.false_blk else ''
        ift = ifs.true_blk.unparsed if ifs.true_blk else ''
        cond = ifs.cond.unparsed
        ifs.unparsed =  'if({})\n{}\n{}'.format(cond, ift, iff)

    def block(self, b):
        s = [s.unparsed for s in b.stmts]
        b.unparsed = '{' + '\n'.join(s) + '}'

    def funcdef(self, f):
        stmts = [s.unparsed for s in f.stmts]
        args = [p.unparsed for p in f.pars]
        f.unparsed = 'FUNCTION {}({}){{\n\t{}\n}}'.format(f.name, args, stmts)

    def locals(self, loc):
        locs = ', '.join([l.unparsed for l in loc.vars])
        loc.unparsed = 'LOCAL {}'.format(locs)

    def local(self, loc):
        loc.unparsed = loc.name

    def funcpar(self, fp):
        fp.unparsed = fp.name

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
        expression = p.expression.unparsed
        p.unparsed = "{}' = {}".format(var, expression)

    def unparse(self, mod):
        m = self.mm.model_from_str(mod)
        return m.unparsed


