import os
from textx.metamodel import metamodel_from_file


class NModlCompiler(object):
    def __init__(self):
        curr_dir = os.path.dirname(__file__)
        self.mm = metamodel_from_file(
            os.path.join(curr_dir, 'grammar', 'nmodl.tx'),
            auto_init_attributes=False)

        self.mm.register_obj_processors({
            'Program': self.handle_program,

            'Title': self.handle_title,

            # UNITS
            'Units': self.handle_units_blk,
            'UnitDef': self.handle_unit_def,
            'UnitsCtrl': self.handle_unit_ctrl,

            # NEURON
            'Neuron': self.handle_neuron_blk,
            'Suffix': self.handle_suffix,
            'Global': self.handle_global,
            'Range': self.handle_range,
            'Pointer': self.handle_pointer,
            'External': self.handle_external,
            'Nonspecific': self.handle_nonspecific,
            'UseIon': self.handle_useIon,
            'Read': self.handle_read,
            'Write': self.handle_write,
            'Valence': self.handle_valence,

            'Independent': self.handle_indep,

            # PARAMETER
            'Parameter': self.handle_parameter_blk,
            'ParDef': self.handle_param,

            # CONSTANT
            'Constant': self.handle_const_blk,
            'ConstDef': self.handle_const,

            # ASSIGNED
            'Assigned': self.handle_assigned_blk,
            'AssignedDef': self.handle_assigned,

            # STATE
            'StateVariable': self.handle_state_variable,
            'State': self.handle_state_blk,

            # BREAKPOINT
            'Breakpoint': self.handle_breakpoint_blk,
            'Solve': self.handle_solve,

            # INITIAL
            'Initial': self.handle_initial_blk,

            # DERIVATIVE
            'Derivative': self.handle_derivative_blk,

            # FUNCTION - PROCEDURE
            'FuncsProcs': self.handle_funcsprocs,

            # expression-related
            'Table': self.handle_table,
            'From': self.handle_from,
            'To': self.handle_to,
            'With': self.handle_with,
            'SafeVar': self.handle_safevar,
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

            'Threadsafe': self.handle_threadsafe
        })

    def handle_title(self, node):
        pass

    def handle_units_blk(self, node):
        pass

    def handle_unit_ctrl(self, node):
        pass

    def handle_state_blk(self, node):
        pass

    def handle_state_variable(self, node):
        pass

    def handle_unit_def(self, node):
        pass

    def handle_funcsprocs(self, node):
        pass

    def handle_program(self, prog):
        def blocks_of_type(blocks, typename):
            return [b for b in blocks if type(b).__name__ == typename]

        for b in ('Title', 'Units', 'Neuron', 'Parameter', 'Assigned',
                  'State', 'Initial', 'Breakpoint', 'Derivative'):
            blks = blocks_of_type(prog.blocks, b)
            if len(blks) > 1:
                # TODO: proper validation 
                print('Validation error:', 'multiple {} blocks'
                      .format(b.capitalize))
                exit(1)
            else:
                if blks:
                    setattr(prog, b.lower(), blks[0])

    def handle_suffix(self, node):
        pass

    def handle_global(self, glob):
        pass

    def handle_range(self, range):
        pass

    def handle_pointer(self, pointer):
        pass

    def handle_external(self, external):
        pass

    def handle_nonspecific(self, nonspecific):
        pass

    def handle_useIon(self, useIon):
        pass

    def handle_read(self, node):
        pass

    def handle_write(self, node):
        pass

    def handle_valence(self, node):
        pass

    def handle_parameter_blk(self, pblk):
        pass

    def handle_param(self, node):
        pass

    def handle_const_blk(self, pblk):
        pass

    def handle_const(self, node):
        pass

    def handle_assigned_blk(self, pblk):
        pass

    def handle_assigned(self, node):
        pass

    def handle_neuron_blk(self, node):
        pass

    def handle_breakpoint_blk(self, node):
        pass

    def handle_solve(self, node):
        pass

    # expression-related
    #
    def handle_table(self, node):
        pass

    def handle_from(self, node):
        pass

    def handle_to(self, node):
        pass

    def handle_with(self, node):
        pass

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

    def handle_derivative_blk(self, node):
        pass

    def handle_initial_blk(self, node):
        pass

    def handle_threadsafe(self, node):
        pass

    def handle_indep(self, node):
        pass

    def handle_safevar(self, node):
        pass
