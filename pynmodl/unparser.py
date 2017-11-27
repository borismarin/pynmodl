from textwrap import indent
from pynmodl.nmodl import NModlCompiler


def ind(x):
    return indent(x, '    ')


def blockify(stmts):
    return '\n'.join(['{', ind('\n'.join(s.unparsed for s in stmts)), '}'])


class Unparser(NModlCompiler):

    def unparse_list(self, leest):
        def deref(ref):
            if isinstance(ref, str):
                return ref
            elif type(ref).__name__ == 'SafeVar':
                return ref.var.name
            else:  # should be ref
                return ref.name
        return ', '.join(deref(el) for el in leest)

    def handle_program(self, prog):
        super().handle_program(prog)
        prog.unparsed = '\n'.join(b.unparsed for b in prog.blocks)

    def handle_title(self, tit):
        tit.unparsed = 'TITLE ' + tit.title

    def handle_state_blk(self, st):
        st.unparsed = 'STATE ' + blockify(st.state_vars)

    def handle_state_variable(self, st):
        unit = ' ' + st.unit if st.unit else ''
        st.unparsed = st.name + unit

    # UNITS block
    def handle_units_blk(self, ublk):
        ublk.unparsed = 'UNITS ' + blockify(ublk.unit_defs)

    def handle_unit_def(self, udef):
        base_unit = ''.join(udef.base_units)
        udef.unparsed = ' '.join((udef.name, '=', base_unit))

    def handle_unit_ctrl(self, uc):
        uc.unparsed = 'UNITSON' if uc.units_on else 'UNITSOFF'

    # NEURON block
    def handle_neuron_blk(self, nrn):
        nrn.unparsed = 'NEURON ' + blockify(nrn.statements)

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
        reads = use_ion.r[0].unparsed if use_ion.r else ''
        writes = use_ion.w[0].unparsed if use_ion.w else ''
        valence = use_ion.v[0].unparsed if use_ion.v else ''
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
        pblk.unparsed = 'PARAMETER ' + blockify(pblk.parameters)

    def handle_param(self, pd):
        pd.unparsed = pd.name
        if pd.value:
            pd.unparsed += ' = {:g}'.format(float(pd.value))
        if pd.unit:
            pd.unparsed += ' ' + pd.unit
        if (pd.llim and pd.ulim):
            pd.unparsed += ' <{:g}, {:g}>'.format(float(pd.llim),
                                                  float(pd.ulim))

    # ASSIGNED block
    def handle_assigned_blk(self, ablk):
        ablk.unparsed = 'ASSIGNED ' + blockify(ablk.assigneds)

    def handle_assigned(self, ad):
        unit = ad.unit if ad.unit else ''
        ad.unparsed = ' '.join((ad.name, unit)).rstrip()

    # BREAKPOINT BLOCK
    def handle_breakpoint_blk(self, bp):
        bp.unparsed = 'BREAKPOINT ' + blockify(bp.b.stmts)

    def handle_solve(self, solve):
        meth = ' METHOD ' + solve.method if solve.method else ''
        solve.unparsed = 'SOLVE ' + solve.solve.name + meth

    # DERIVATIVE
    def handle_derivative_blk(self, deriv):
        head = ' '.join(('DERIVATIVE', deriv.name, ''))
        deriv.unparsed = head + blockify(deriv.b.stmts)

    # INITIAL
    def handle_initial_blk(self, init):
        init.unparsed = 'INITIAL ' + blockify(init.b.stmts)

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
        b.unparsed = blockify(b.stmts)

    def handle_funcdef(self, f):
        stmts = f.b.unparsed
        args = ', '.join([p.unparsed for p in f.pars])
        f_or_p = 'FUNCTION' if f.is_function else 'PROCEDURE'
        f.unparsed = '{} {}({}){}'.format(f_or_p, f.name, args, stmts)

    def handle_locals(self, loc):
        locs = self.unparse_list(loc.vars)
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

    def handle_table(self, table):
        unp = 'TABLE ' + self.unparse_list(table.tabbed)
        if table.depend:
            unp += ' DEPEND ' + self.unparse_list(table.depend.deps)
        table.unparsed = ' '.join((unp, table.f.unparsed,
                                   table.t.unparsed,
                                   table.w.unparsed))

    def handle_to(self, to):
        fmt = '{}' if isinstance(to.val, str) else '{:g}'
        to.unparsed = 'TO ' + fmt.format(to.val)

    def handle_from(self, fro):
        fmt = '{}' if isinstance(fro.val, str) else '{:g}'
        fro.unparsed = 'FROM ' + fmt.format(fro.val)

    def handle_with(self, wit):
        wit.unparsed = 'WITH ' + str(wit.val)

    def handle_primed(self, p):
        var = p.variable
        expression = p.expression.unparsed
        p.unparsed = "{}' = {}".format(var, expression)

    def handle_threadsafe(self, t):
        t.unparsed = 'THREADSAFE'

    def handle_indep(self, ind):
        ind.unparsed = "INDEPENDENT {{{} FROM {:g} TO {:g} WITH {:g}".format(
            ind.name, ind.f, ind.t, ind.w)
        if ind.s:
            ind.unparsed += 'START ' + ind.s
        if ind.u:
            ind.unparsed += ' ' + ind.u
        ind.unparsed += '}'

    def compile(self, mod):
        m = self.mm.model_from_str(mod)
        return m.unparsed
