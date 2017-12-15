import os
from textx.metamodel import metamodel_from_file
from textx.model import children_of_type, parent_of_type


def handle_refs(model, metamodel):
    def enclosing_block(node):
        return parent_of_type('Block', node) or \
                parent_of_type('SolvableBlock', node)

    def enclosing_func(node):
        return parent_of_type('FuncDef', ref)

    for ref in children_of_type('VarRef', model):
        found = 0
        scopes = [children_of_type('Local', enclosing_block(ref)),
                  children_of_type('FuncPar', enclosing_func(ref)),
                  children_of_type('StateVariable', model),
                  children_of_type('ParDef', model),
                  children_of_type('AssignedDef', model),
                  children_of_type('ConstDef', model)]
        for scope in scopes:
            for var in scope:
                if var.name == ref.var.name:
                    ref.var = var
                    found = True
                    break
            if found:
                break


mm = metamodel_from_file(
    os.path.join(os.path.dirname(__file__), '../../grammar/nmodl.tx'))
mm.register_model_processor(handle_refs)


def refs_in(node):
    return children_of_type('VarRef', node)


def test_scoping():
    p = """
        PARAMETER {
            v (mV)
        }

        STATE { x }

        INITIAL {
            LOCAL v
            v = 10
            x = -v : v is local
        }

        FUNCTION f(v) {
            f = -v : v is funcpar
        }

        DERIVATIVE dx {
            x' = f(x) + v : v is par
        }

        """
    blocks = mm.model_from_str(p).blocks
    (parameter, state, initial, function_f, derivative) = blocks

    locals_in_init = children_of_type('Local', initial)
    assert refs_in(initial)[0].var == locals_in_init[0]

    assert type(refs_in(function_f)[-1].var).__name__ == 'FuncPar'

    assert refs_in(derivative)[-1].var == parameter.parameters[0]
