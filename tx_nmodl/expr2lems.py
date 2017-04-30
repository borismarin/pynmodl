from tx_nmodl.expr_compiler import ExprCompiler
from textx.model import parent_of_type

META_TMP = '{{{}}}'
F_VAR_TMP = '_'.join(['{}', META_TMP, META_TMP])
LOCAL_TMP = F_VAR_TMP + '__{}'


class Lems(ExprCompiler):

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

    def mangle_name(self, root, pars, suff=None):
        par_ph = ['{' + p.name + '}' for p in pars]
        s = '__{}'.format(suff) if suff else ''
        return '{}_{}'.format(root, '_'.join(par_ph)) + s

    def varref(self, var):
        ivar = var.var
        if(self.is_txtype(ivar, 'FuncPar')):
            lems = '{{{}}}'.format(ivar.name)
        elif(self.is_txtype(ivar, 'FuncDef')):
            lems = self.mangle_name(ivar.name, ivar.pars)
        elif(self.is_txtype(ivar, 'Local')):
            parent = parent_of_type('FuncDef', ivar)
            lems = self.mangle_name(parent.name, parent.pars, ivar.name)
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
        if f.func.builtin:
            fun = f.func.builtin
            f.deps = ''
            lems = '{}({})'.format(fun, ', '.join(args))
        else:
            fun = f.func.user
            arg_val = dict(zip([p.name for p in fun.pars], args))
            f.deps = fun.template.format(**arg_val)
            if fun.is_function:
                lems = '{}_{}'.format(fun.name, '_'.join(args))
            elif fun.is_procedure:
                lems = f.deps
        f.lems = lems

    def assign(self, asgn):
        var = asgn.variable
        exp = asgn.expression
        deps = self.func_deps(exp)
        if var:
            asgn.lems = deps +\
                    '<DerivedVariable name="{}" value="{}"/>'.format(
                        var.lems, exp.lems)
        else:
            asgn.lems = exp.lems

    def ifstmt(self, ifs):
        iff = 'else\n' + ifs.false_blk.lems if ifs.false_blk else ''
        ift = ifs.true_blk.lems if ifs.true_blk else ''
        cond = ifs.cond.lems
        ifs.lems = '<CondDerVar>\n\t<Case cond="{}">\n<Case{}'.format(
            cond, ift, iff)

    def block(self, b):
        b.lems = ''.join([s.lems for s in b.stmts])

    def funcdef(self, f):
        stmts = [s.lems for s in f.b.stmts]
        args = [p.lems for p in f.pars]
        f.lems = ''
        f.template = self.func_template(f, stmts, args)

    def func_template(self, f, stmts, args):
        from itertools import compress
        is_asgn = map(lambda el: self.is_txtype(el, 'Assignment'), f.b.stmts)
        asgns = [s for s in compress(stmts, is_asgn)]
        return '\n'.join(asgns)

    def func_deps(self, node):
        from textx.model import children_of_type
        fcalls = children_of_type('FuncCall', node)
        return '\n'.join([fc.deps for fc in fcalls] + [''])

    def locals(self, loc):
        loc.lems = ''

    def local(self, loc):
        parent = parent_of_type('FuncDef', loc)
        locname = self.mangle_name(parent.name, parent.pars, loc.name)
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

    def compile(self, mod):
        m = self.mm.model_from_str(mod)
        return m.lems
