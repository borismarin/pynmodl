from xml.etree.ElementTree import Element, tostring
from xml.dom.minidom import parseString
from textx.model import children_of_type, parent_of_type

from pynmodl.nmodl import NModlCompiler
from pynmodl.lems_helpers import ComponentTypeHelper, ComponentHelper


class LemsCompTypeGenerator(NModlCompiler):

    def __init__(self):
        super().__init__()
        self.L = ComponentTypeHelper()
        self.mm.register_model_processor(self.add_block_bodies)
        self.mm.register_model_processor(self.add_derivatives)

    def handle_suffix(self, suf):
        self.L.comp_type.attrib['id'] = suf.suffix + '_lems'

    def handle_read(self, read):
        for r in read.reads:
            self.L.req(r.name, 'none')

    def handle_write(self, write):
        for w in write.writes:
            self.L.exp(w.name, 'none')

    def handle_param(self, pardef):
        pname = pardef.name
        if pname in ['v', 'celsius']:
            self.L.req(pname, 'none')
        else:
            self.L.par(pname, 'none')

    def handle_state_variable(self, state):
        self.L.exp(state.name, 'none')
        self.L.state(state.name, 'none')

    def handle_assign(self, asgn):
        var = asgn.variable
        exp = asgn.expression
        if not var:
            asgn.lems = exp.lems
        asgn.visited = False

    def mangle_name(self, root, pars, suff=None):
        par_ph = ['{' + p.name + '}' for p in pars]
        s = '__{}'.format(suff) if suff else ''
        return '{}_{}'.format(root, '_'.join(par_ph)) + s

    def handle_varref(self, var):
        ivar = var.var
        if type(ivar).__name__ == 'FuncPar':
            lems = '{{{}}}'.format(ivar.name)
        elif type(ivar).__name__ == 'FuncDef':
            lems = self.mangle_name(ivar.name, ivar.pars)
        elif type(ivar).__name__ == 'Local':
            parent = parent_of_type('FuncDef', ivar)
            lems = self.mangle_name(parent.name, parent.pars, ivar.name)
        else:
            lems = ivar.name
        var.lems = lems

    #  function def related methods

    def handle_funcdef(self, f):
        if not getattr(f, 'visited_with_args', False):
            f.visited_with_args = []

    def handle_local(self, loc):
        parent = parent_of_type('FuncDef', loc)
        locname = self.mangle_name(parent.name, parent.pars, loc.name)
        loc.lems = locname

    def handle_funcpar(self, fp):
        fp.lems = fp.name

    def handle_funccall(self, fc):
        args = [a.lems for a in fc.args]
        if fc.func.builtin:
            fun = fc.func.builtin
            lems = '{}({})'.format(fun, ', '.join(args))
        else:
            fun = fc.func.user
            if fun.is_function:
                lems = '{}_{}'.format(fun.name, '_'.join(args))
            elif fun.is_procedure:
                lems = ''
        fc.lems = lems

    # methods below pertain to nodes handled by direct string generation
    def binop(self, node):
        ops = [n.lems for n in node.op[1:]]
        l = node.op[0].lems
        node.lems = l + ''.join(ops)

    def op(self, op):
        op.lems = ' ' + self.L.OPS.get(op.o, op.o) + ' '

    def handle_negation(self, neg):
        s = neg.sign.lems if neg.sign else ''
        v = neg.primary.lems
        neg.lems = s + v

    def handle_paren(self, par):
        par.lems = '(' + par.ex.lems + ')'

    def handle_addition(self, add):
        self.binop(add)

    def handle_multiplication(self, mul):
        self.binop(mul)

    def handle_exponentiation(self, exp):
        self.binop(exp)

    def handle_num(self, num):
        num.lems = num.num

    def handle_pm(self, pm):
        self.op(pm)

    def handle_md(self, md):
        self.op(md)

    def handle_exp(self, exp):
        self.op(exp)

    def handle_relational(self, l):
        self.binop(l)

    def handle_logicalcon(self, l):
        self.binop(l)

    def handle_logcon(self, l):
        self.op(l)

    def handle_relop(self, r):
        self.op(r)

    # _Model_ processors (all above are node listeners)

    def process_block(self, root, context={}):
        import functools

        def asgn_var(asgn):
            return functools.reduce(getattr, [asgn, 'variable', 'var'])

        def inner_asgns(x):
            return (a for a in children_of_type('Assignment', x)
                    if a.variable)

        # handle if blocks separately (cond deriv vars)
        nonif_asgns = (a for a in inner_asgns(root)
                       if not parent_of_type('IfStatement', a))
        for asgn in nonif_asgns:
            self.L.dv(asgn.variable.lems.format(**context),
                      asgn.expression.lems.format(**context))

        # paired if/else assignements
        for ifst in children_of_type('IfStatement', root):
            ift_asgns = {asgn_var(a): a for a in inner_asgns(ifst.true_blk)}
            iff_asgns = {asgn_var(a): a for a in inner_asgns(ifst.false_blk)}
            for var in ift_asgns.keys() ^ iff_asgns.keys():
                asgn = ift_asgns.get(var,  iff_asgns.get(var))
                self.L.dv(asgn.variable.lems.format(**context),
                          asgn.expression.lems.format(**context))
            for var in ift_asgns.keys() & iff_asgns.keys():
                tasgn = ift_asgns[var]
                fasgn = iff_asgns[var]
                self.L.cdv(tasgn.variable.lems.format(**context),
                           ifst.cond.lems.format(**context),
                           tasgn.expression.lems.format(**context),
                           fasgn.expression.lems.format(**context))
            # TODO: multiple assignment to same var [x=y if(x<z){x=w}]

    def add_block_bodies(self, model, metamodel):
        # append function body for every function call
        for fc in children_of_type('FuncCall', model):
            if fc.func.user:
                args = [a.lems for a in fc.args]
                fun = fc.func.user
                arg_val = dict(zip([p.name for p in fun.pars], args))
                if args not in fun.visited_with_args:
                    self.process_block(fun, arg_val)
                    fun.visited_with_args.append(args)

    def add_derivatives(self, model, metamodel):
        for p in children_of_type('Primed', model):
            var = p.variable
            expression = p.expression
            self.L.dxdt(var, expression.lems)


    # Utility methods

    def compile(self, model_str):
        self.mm.model_from_str(model_str)
        return self.L.render()

    def compile_to_string(self, model_str):
        '''Render the ComponentType ElementTree as a string'''
        s = parseString(tostring(self.compile(model_str)))
        return s.toprettyxml()


class LemsComponentGenerator(NModlCompiler):
    def __init__(self):
        super().__init__()
        self.mm.register_obj_processors({
            'Suffix': self.handle_suffix,
            'ParDef': self.handle_param,
        })
        self.L = ComponentHelper()
        self.par_vals = {}

    def handle_suffix(self, suff):
        self.L.id = suff.suffix + '_lems'

    def handle_param(self, pardef):
        self.L.par_vals[pardef.name] = str(pardef.value)

    def compile(self, model_str):
        '''Generate an ElementTree describing a Lems ComponentType'''
        self.mm.model_from_str(model_str)
        return self.L.render()

    def compile_to_string(self, model_str):
        '''Render the ComponentType ElementTree as a string'''
        s = parseString(tostring(self.compile(model_str)))
        return s.toprettyxml()


def mod2lems(mod_string):

    root = Element('neuroml')
    root.append(LemsCompTypeGenerator().compile(mod_string))
    root.append(LemsComponentGenerator().compile(mod_string))

    return tostring(root)
