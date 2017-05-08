from textwrap import indent
from pynmodl.nmodl import NModlCompiler


def ind(x):
    return indent(x, '\t')


def blockify(stmts):
    return '\n'.join(['{', ind('\n'.join(stmts)), '}'])


class Unparser(NModlCompiler):

    def handle_program(self, prog):
        prog.unparsed = '\n'.join([getattr(prog, at).unparsed
                                   for at in prog._tx_attrs
                                   if getattr(prog, at)])

    def handle_funcsprocs(self, fps):
        fps.unparsed = '\n'.join([f.unparsed for f in fps.fd])

    def binop(self, node):
        ops = [n.unparsed for n in node.op[1:]]
        l = node.op[0].unparsed
        node.unparsed = l + ''.join(ops)

    def op(self, op):
        op.unparsed = ' ' + op.o + ' '

    def handle_addition(self, add):
        self.binop(add)

    def handle_multiplication(self, mul):
        self.binop(mul)

    def handle_exponentiation(self, exp):
        self.binop(exp)

    def handle_negation(self, neg):
        s = neg.sign.o if neg.sign else ''
        v = neg.primary.unparsed
        neg.unparsed = s + v

    def handle_paren(self, par):
        p = par.ex.unparsed
        par.unparsed = '(' + p + ')'

    def handle_num(self, num):
        num.unparsed = num.num

    def handle_varref(self, var):
        var.unparsed = var.var.name

    def handle_pm(self, pm):
        self.op(pm)

    def handle_md(self, md):
        self.op(md)

    def handle_exp(self, exp):
        self.op(exp)

    def handle_funccall(self, f):
        args = [a.unparsed for a in f.args]
        if f.func.builtin:
            fname = f.func.builtin
        else:
            fname = f.func.user.name
        f.unparsed = '{}({})'.format(fname, ', '.join(args))

    def handle_assign(self, asgn):
        var = asgn.variable
        exp = asgn.expression
        if var:
            asgn.unparsed = '{} = {}'.format(var.unparsed, exp.unparsed)
        else:
            asgn.unparsed = exp.unparsed

    def handle_ifstmt(self, ifs):
        iff = 'else' + ifs.false_blk.unparsed if ifs.false_blk else ''
        ift = ifs.true_blk.unparsed if ifs.true_blk else ''
        cond = ifs.cond.unparsed
        ifs.unparsed = 'if({}){}{}'.format(cond, ift, iff)

    def handle_block(self, b):
        b.unparsed = blockify([s.unparsed for s in b.stmts])

    def handle_funcdef(self, f):
        stmts = f.b.unparsed
        args = ', '.join([p.unparsed for p in f.pars])
        f.unparsed = 'FUNCTION {}({}){}'.format(f.name, args, stmts)

    def handle_locals(self, loc):
        locs = ', '.join([l.unparsed for l in loc.vars])
        loc.unparsed = 'LOCAL {}'.format(locs)

    def handle_local(self, loc):
        loc.unparsed = loc.name

    def handle_funcpar(self, fp):
        fp.unparsed = fp.name

    def handle_relational(self, l):
        self.binop(l)

    def handle_logicalcon(self, l):
        self.binop(l)

    def handle_logcon(self, l):
        self.op(l)

    def handle_relop(self, r):
        self.op(r)

    def handle_primed(self, p):
        var = p.variable
        expression = p.expression.unparsed
        p.unparsed = "{}' = {}".format(var, expression)

    def compile(self, mod):
        m = self.mm.model_from_str(mod)
        return m.unparsed
