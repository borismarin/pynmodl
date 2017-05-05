from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from tx_nmodl.nmodl import NModl
from textx.model import children_of_type, parent_of_type


class LemsCompTypeGenerator(NModl):
    ops = {'>': '.gt.', '>=': '.geq.', '<': '.lt.', '<=': '.leq.',
           '!=': '.neq.', '==': '.eq.', '&&': '.and.', '||': '.or.'}

    def __init__(self):
        super().__init__()
        self.mm.register_obj_processors({
            'Suffix': self.handle_suffix,
            'Read': self.handle_read,
            'Write': self.handle_write,
            'ParDef': self.handle_param,
            'StateVariable': self.handle_state,
            # expression-related
            'Addition': self.handle_addition,
            'Multiplication': self.handle_multiplication,
            'Exponentiation': self.handle_exponentiation,
            'Negation': self.handle_negation,
            'Paren': self.handle_paren,
            'FuncCall': self.handle_funccall,
            'Num': self.handle_num,
            'VarRef': self.handle_varref,
            'PlusOrMinus': self.handle_pm,
            'MulOrDiv': self.handle_md,
            'Exp': self.handle_exp,
            'Assignment': self.handle_assign,
            'IfStatement': self.handle_ifstmt,
            'Relational': self.handle_relational,
            'LogicalCon': self.handle_logicalcon,
            'Block': self.handle_block,
            'RelOp': self.handle_relop,
            'LogCon': self.handle_logcon,
            'FuncDef': self.handle_funcdef,
            'Locals': self.handle_locals,
            'FuncPar': self.handle_funcpar,
            'Primed': self.handle_primed,
            'Local': self.handle_local,
        })
        self.xml_skeleton()

    def handle_suffix(self, suf):
        self.comp_type.attrib['id'] = suf.suffix

    def handle_read(self, read):
        for r in read.reads:
            self.subel('Requirement', {'name': r.name, 'dimension': 'none'})

    def handle_write(self, write):
        for w in write.writes:
            self.subel('Exposure', {'name': w.name, 'dimension': 'none'})

    def handle_param(self, pardef):
        self.subel('Parameter', {'name': pardef.name, 'dimension': 'none'})

    def handle_state(self, state):
        self.subel('Exposure', {'name': state.name, 'dimension': 'none'})
        self.subel('StateVariable', {'name': state.name, 'dimension': 'none'})

    def handle_block(self, b):
        if not (parent_of_type('FuncDef', b) or
                children_of_type('FuncCall', b)):
            self.process_block(b)

    def handle_assign(self, asgn):
        var = asgn.variable
        exp = asgn.expression
        if not var:
            asgn.lems = exp.lems
        asgn.visited = False

    def handle_ifstmt(self, ifs):
        pass

    def handle_primed(self, p):
        var = p.variable
        expression = p.expression
        self.dxdt(var, expression.lems)

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

    def process_block(self, root, context={}):
        def inner_asgns(x):
            return (a for a in children_of_type('Assignment', x)
                    if a.variable)
        for ifst in children_of_type('IfStatement', root):
            # handling true/false assignments for the same var
            for t, f in zip(inner_asgns(ifst.true_blk),
                            inner_asgns(ifst.false_blk)):
                if t.variable.var == f.variable.var:
                    self.cdv(t.variable.lems.format(**context),
                             ifst.cond.lems.format(**context),
                             t.expression.lems.format(**context),
                             f.expression.lems.format(**context))
                    t.visited = True
                    f.visited = True
            # TODO: multiple assignement to same var [x=y if(x<z){x=w}]
        for asgn in inner_asgns(root):
            if not asgn.visited:
                self.dv(asgn.variable.lems.format(**context),
                        asgn.expression.lems.format(**context))

    #  function def related methods

    def handle_funcdef(self, f):
        if not getattr(f, 'visited_with_args', False):
            f.visited_with_args = []

    def handle_locals(self, loc):
        pass

    def handle_local(self, loc):
        parent = parent_of_type('FuncDef', loc)
        locname = self.mangle_name(parent.name, parent.pars, loc.name)
        loc.lems = locname

    def handle_funcpar(self, fp):
        fp.lems = fp.name

    def visit_down(self, model_obj):
        MULT_ONE = '1'
        PRIMITIVE_PYTHON_TYPES = [int, float, str, bool]

        if type(model_obj) in PRIMITIVE_PYTHON_TYPES:
            metaclass = type(model_obj)
        else:
            metaclass = self.mm[model_obj.__class__.__name__]
            for metaattr in metaclass._tx_attrs.values():
                # If attribute is containment reference go down
                if metaattr.ref and metaattr.cont:
                    attr = getattr(model_obj, metaattr.name)
                    if attr:
                        if metaattr.mult != MULT_ONE:
                            for obj in attr:
                                if obj:
                                    self.visit_down(obj)
                        else:
                            self.visit_down(attr)
        obj_processor = self.mm.obj_processors.get(metaclass.__name__, None)
        if obj_processor:
            obj_processor(model_obj)

    def handle_funccall(self, fc):
        args = [a.lems for a in fc.args]
        if fc.func.builtin:
            fun = fc.func.builtin
            lems = '{}({})'.format(fun, ', '.join(args))
        else:
            fun = fc.func.user
            if not getattr(fun, 'visited', False):  # handle posterior decl
                self.visit_down(fun)
                fun.visited = True
            arg_val = dict(zip([p.name for p in fun.pars], args))
            if fun.is_function:
                lems = '{}_{}'.format(fun.name, '_'.join(args))
            elif fun.is_procedure:
                lems = ''  # only interested in side effects handled below
            if args not in fun.visited_with_args:
                self.process_block(fun, arg_val)
                fun.visited_with_args.append(args)
        fc.lems = lems

    # methods below pertain to nodes handled by direct string generation
    def binop(self, node):
        ops = [n.lems for n in node.op[1:]]
        l = node.op[0].lems
        node.lems = l + ''.join(ops)

    def op(self, op):
        op.lems = ' ' + self.ops.get(op.o, op.o) + ' '

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

    def subel(self, type, attrs):
        return SubElement(self.where[type], type, attrib=attrs)

    def dv(self, name, val):
        SubElement(self.dynamics, 'DerivedVariable',
                   attrib={'name': name, 'value': val})

    def dxdt(self, var, val):
        SubElement(self.dynamics, 'TimeDerivative',
                   attrib={'variable': var, 'value': val})

    def cdv(self, name, cond, if_true, if_false):
        cdv = SubElement(self.dynamics, 'ConditionalDerivedVariable',
                         attrib={'name': name})
        SubElement(cdv, 'Case', attrib={'condition': cond, 'value': if_true})
        SubElement(cdv, 'Case', attrib={'value': if_false})

    def compile(self, model_str):
        self.mm.model_from_str(model_str)
        self.comp_type.append(self.dynamics)
        return self.comp_type

    def xml_skeleton(self):
        self.comp_type = Element('ComponentType', attrib={
            'extends': 'baseIonChannel'})
        self.comp_type.append(
            Comment('The defs below are hardcoded for testing purposes!'))
        SubElement(self.comp_type, 'Constant', attrib={
            'dimension': 'voltage', 'name': 'MV', 'value': '1mV'})
        SubElement(self.comp_type, 'Constant', attrib={
            'dimension': 'time', 'name': 'MS', 'value': '1ms'})
        SubElement(self.comp_type, 'Requirement', attrib={
            'name': 'v', 'dimension': 'voltage'})
        self.comp_type.append(Comment('End of hardcoded defs!'))
        self.dynamics = Element('Dynamics')
        self.where = {'Parameter': self.comp_type, 'Requirement':
                      self.comp_type, 'Exposure': self.comp_type,
                      'DerivedVariable': self.dynamics, 'StateVariable':
                      self.dynamics}


class LemsComponentGenerator(NModl):
    def __init__(self):
        super().__init__()
        self.mm.register_obj_processors({
            'Suffix': self.handle_suffix,
            'ParDef': self.handle_param,
        })
        self.par_vals = {}

    def handle_suffix(self, suff):
        self.id = suff.suffix + '_lems'

    def handle_param(self, pardef):
        self.par_vals[pardef.name] = str(pardef.value)

    def compile(self, model_str):
        self.mm.model_from_str(model_str)
        comp_attr = {'id': self.id}
        comp_attr.update(self.par_vals)
        return Element(self.id, attrib=comp_attr)


def mod2lems(mod_string):

    root = Element('neuroml')
    root.append(LemsCompTypeGenerator().compile(mod_string))
    root.append(LemsComponentGenerator().compile(mod_string))

    return tostring(root)
