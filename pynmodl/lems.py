import functools
from xml.etree.ElementTree import Element, tostring
from xml.dom.minidom import parseString
from itertools import count
from textx.model import children_of_type, parent_of_type

from pynmodl.nmodl import NModlCompiler
from pynmodl.lems_helpers import ComponentTypeHelper, ComponentHelper
import pynmodl.model_utils as mu


class LemsCompTypeGenerator(NModlCompiler):

    def __init__(self):
        super().__init__()
        self.L = ComponentTypeHelper()
        self.mm.register_model_processor(self.add_block_bodies)
        self.mm.register_model_processor(self.add_derivatives)
        self._arg_counter = count()
        self.generated_aux = []

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

    def mangle_name(self, root, pars, suff=None):
        par_ph = [''] + ['{' + p.name + '}' for p in pars]
        s = '::{}'.format(suff) if suff else ''
        return root + '_'.join(par_ph) + s

    def handle_varref(self, var):
        super().handle_varref(var)
        ivar = var.var
        if type(ivar).__name__ == 'FuncPar':
            lems = '{{{}}}'.format(ivar.name)
        elif type(ivar).__name__ == 'FuncDef':
            lems = self.mangle_name(ivar.name, ivar.pars)
        elif type(ivar).__name__ == 'Local':
            # there be dragons: 'if' blocks, for example, don't have names...
            in_block = parent_of_type('Block', ivar)
            parent = in_block.parent
            lems = self.mangle_name(parent.name,
                                    getattr(parent, 'pars', []), ivar.name)
        else:
            lems = ivar.name
        var.lems = lems

    #  function def related methods

    def handle_funcdef(self, f):
        if not getattr(f, 'visited_with_args', False):
            f.visited_with_args = []

    def handle_local(self, loc):
        in_block = parent_of_type('Block', loc)
        parent = in_block.parent
        locname = self.mangle_name(parent.name,
                                   getattr(parent, 'pars', []), loc.name)
        loc.lems = locname

    def handle_funcpar(self, fp):
        fp.lems = fp.name

    def handle_funccall(self, fc):
        if getattr(fc, 'aux_vars', None) is None:
            fc.aux_vars = {}

        def make_aux():
            return '_aux' + str(next(self._arg_counter))

        def process_func_args(func_args):
            args = []  # compiled args
            for arg in func_args:
                if mu.is_composite(arg) and not mu.has_func_calls(arg):
                    # if there are inner func calls, auxs are already processed
                    if arg.lems not in fc.aux_vars.keys():
                        auxname = make_aux()
                        args.append(auxname)
                        fc.aux_vars[arg.lems] = auxname
                else:
                    args.append(arg.lems)
            return args
        if fc.func.builtin:
            fun = fc.func.builtin
            lems = '{}({})'.format(fun, ', '.join(arg.lems for arg in fc.args))
        else:
            args = process_func_args(fc.args)
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
        num.lems = str(num.num)

    def handle_pm(self, pm):
        if type(pm.parent).__name__ == 'Addition':
            self.op(pm)
        else:  # unary pm
            pm.lems = pm.o

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

    # **Model** processors (all above are node listeners)

    def process_block(self, root, context={}):
        def asgn_var(asgn):
            return functools.reduce(getattr, [asgn, 'variable', 'var'])

        def inner_asgns(x):
            return (a for a in children_of_type('Assignment', x)
                    if a.variable)

        nonif_asgns = (a for a in inner_asgns(root)
                       if not parent_of_type('IfStatement', a))
        # handle if blocks separately due to Conditional Derived Variables
        for asgn in nonif_asgns:
            self.L.dv(asgn.variable.lems.format(**context),
                      asgn.expression.lems.format(**context))

        for ifst in children_of_type('IfStatement', root):
            ift_asgns = {asgn_var(a): a for a in inner_asgns(ifst.true_blk)}
            iff_asgns = {asgn_var(a): a for a in inner_asgns(ifst.false_blk)}
            for var in ift_asgns.keys() ^ iff_asgns.keys():
                # unpaired assignements on either if or else block
                asgn = ift_asgns.get(var,  iff_asgns.get(var))
                self.L.dv(asgn.variable.lems.format(**context),
                          asgn.expression.lems.format(**context))
            for var in ift_asgns.keys() & iff_asgns.keys():
                # paired if/else assignements
                tasgn = ift_asgns[var]
                fasgn = iff_asgns[var]
                self.L.cdv(tasgn.variable.lems.format(**context),
                           ifst.cond.lems.format(**context),
                           tasgn.expression.lems.format(**context),
                           fasgn.expression.lems.format(**context))
            # TODO: multiple assignment to same var [x=y if(x<z){x=w}]

    def process_user_func(self, func_call, scope={}):
        # nested funcs need to access parent scope for arg passing
        # (if scope is present, it is being processed from the parent)
        # aux_vars are also inherited from parents
        if parent_of_type('FuncDef', func_call) and not scope:
            return

        args = []  # handle expressions in args that became aux variables
        for arg in func_call.args:
            try:
                args.append(func_call.aux_vars[arg.lems])
            except KeyError:
                args.append(arg.lems)

        fun = func_call.func.user
        arg_val = dict(zip([p.name for p in fun.pars], args))

        if scope:
            for val, arg in arg_val.items():
                arg_val[val] = arg.format(**scope)

        for val, aux_var in func_call.aux_vars.items():
            if aux_var not in self.generated_aux:
                self.L.dv(aux_var, val.format(**arg_val, **scope))
                self.generated_aux.append(aux_var)

        # if the function being called calls other funcs, process them
        for cfc in children_of_type('FuncCall', fun):
            if cfc.func.user:  # catch funcs and procedures, not builtins
                self.process_user_func(cfc, arg_val)

        if args not in fun.visited_with_args:
            self.process_block(fun, arg_val)
            fun.visited_with_args.append(args)

    def add_block_bodies(self, model, metamodel):
        # derivative blocks
        for dx in children_of_type('Derivative', model):
            self.process_block(dx)

        # append function body for every function/procedure call
        for fc in children_of_type('FuncCall', model):
            if fc.func.user:
                self.process_user_func(fc)

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
