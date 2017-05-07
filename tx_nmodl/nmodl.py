import os
from textx.metamodel import metamodel_from_file


class NModlCompiler(object):
    def __init__(self):
        curr_dir = os.path.dirname(__file__)
        self.mm = metamodel_from_file(
            os.path.join(curr_dir, 'grammar', 'nmodl.tx'))

        self.mm.register_obj_processors({
            # NEURON
            'Suffix': self.handle_suffix,
            'Read': self.handle_read,
            'Write': self.handle_write,
            'ParDef': self.handle_param,
            'StateVariable': self.handle_state,

            'Program': self.handle_program,
            'FuncsProcs': self.handle_funcsprocs,

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

    def handle_funcsprocs(self, node):
        pass

    def handle_program(self, node):
        pass

    def handle_suffix(self, node):
        pass

    def handle_read(self, node):
        pass

    def handle_write(self, node):
        pass

    def handle_param(self, node):
        pass

    def handle_state(self, node):
        pass

    # expression-related
    def handle_addition(self, node):
        pass

    def handle_multiplication(self, node):
        pass

    def handle_exponentiation(self, node):
        pass

    def handle_negation(self, node):
        pass

    def handle_paren(self, node):
        pass

    def handle_funccall(self, node):
        pass

    def handle_num(self, node):
        pass

    def handle_varref(self, node):
        pass

    def handle_pm(self, node):
        pass

    def handle_md(self, node):
        pass

    def handle_exp(self, node):
        pass

    def handle_assign(self, node):
        pass

    def handle_ifstmt(self, node):
        pass

    def handle_relational(self, node):
        pass

    def handle_logicalcon(self, node):
        pass

    def handle_block(self, node):
        pass

    def handle_relop(self, node):
        pass

    def handle_logcon(self, node):
        pass

    def handle_funcdef(self, node):
        pass

    def handle_locals(self, node):
        pass

    def handle_funcpar(self, node):
        pass

    def handle_primed(self, node):
        pass

    def handle_local(self, node):
        pass
