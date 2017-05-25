from textwrap import indent
from pynmodl.nmodl import NModlCompiler


def ind(x):
    return indent(x, '    ')


def blockify(stmts):
    return '\n'.join(['{', ind('\n'.join(stmts)), '}'])


class Unparser(NModlCompiler):
    def unparse_attrs(self, node):
        return [getattr(node, at).unparsed
                for at in node._tx_attrs
                if getattr(node, at)]

    def unparse_list(self, leest):
        def deref(ref):
            if isinstance(ref, str):
                return ref
            else:  # should be ref
                return ref.name
        return ', '.join(deref(el) for el in leest)

    def handle_program(self, prog):
        prog.unparsed = '\n'.join(self.unparse_attrs(prog))

    # UNITS block
    def handle_units_blk(self, ublk):
        ublk.unparsed = 'UNITS {}'.format(
            blockify(ud.unparsed for ud in ublk.unit_defs))

    def handle_unit_def(self, udef):
        udef.unparsed = ' '.join((udef.name, '=', udef.base_unit))

    # NEURON block
    def handle_neuron_blk(self, nrn):
        sts = blockify(st.unparsed for st in nrn.statements)
        nrn.unparsed = 'NEURON {}'.format(sts)

    def handle_suffix(self, suff):
        suff.unparsed = 'SUFFIX ' + suff.suffix

    def handle_global(self, glob):
        glob.unparsed = 'GLOBAL ' + self.unparse_list(glob.globals)

    def handle_range(self, range):
        range.unparsed = 'RANGE ' + self.unparse_list(range.ranges)

    def handle_pointer(self, pointer):
        pointer.unparsed = 'POINTER ' + self.unparse_list(pointer.pointers)

    def handle_external(self, ext):
        # External: 'EXTERNAL' externals+=ID[','];
        ext.unparsed = 'EXTERNAL ' + self.unparse_list(ext.externals)

    def handle_nonspecific(self, nonspec):
        nonspec.unparsed = 'NONSPECIFIC_CURRENT ' + self.unparse_list(
            nonspec.nonspecifics)

    def handle_useIon(self, use_ion):
        # UseIon: 'USEION' ion=ID (r=Read | w=Write | v=Valence)*;
        ion = 'USEION ' + use_ion.ion
        reads = use_ion.r.unparsed if use_ion.r else ''
        writes = use_ion.w.unparsed if use_ion.w else ''
        valence = use_ion.v.unparsed if use_ion.v else ''
        use_ion.unparsed = ' '.join([ion, reads, writes, valence]).rstrip()

    def handle_read(self, read):
        read.unparsed = 'READ ' + self.unparse_list(read.reads)
        pass

    def handle_write(self, write):
        write.unparsed = 'WRITE ' + self.unparse_list(write.writes)
        pass

    def handle_valence(self, valence):
        valence.unparsed = 'VALENCE ' + '{0:+}'.format(valence.valence)

    def handle_funcsprocs(self, fps):
        fps.unparsed = '\n'.join([f.unparsed for f in fps.fd])

    # PARAMETER block
    def handle_parameter_blk(self, pblk):
        pblk.unparsed = 'PARAMETER {}'.format(
            blockify(p.unparsed for p in pblk.parameters))

    def handle_param(self, pd):
        pd.unparsed = pd.name
        if pd.value:
            pd.unparsed += ' = {:g}'.format(pd.value)
        if pd.unit:
            pd.unparsed += ' ' + pd.unit
        if (pd.llim and pd.ulim):
            pd.unparsed += ' <{}, {}>'.format(str(pd.llim), str(pd.ulim))

    # ASSIGNED block
    def handle_assigned_blk(self, ablk):
        ablk.unparsed = 'ASSIGNED {}'.format(
            blockify(a.unparsed for a in ablk.assigneds))

    def handle_assigned(self, ad):
        unit = ad.unit if ad.unit else ''
        ad.unparsed = ' '.join((ad.name, unit)).rstrip()

    # Expressions
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
