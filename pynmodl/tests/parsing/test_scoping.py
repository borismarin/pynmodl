import os
from textx.metamodel import metamodel_from_file
from textx.model import children_of_type
from pynmodl.scoping import scope_processor

mm = metamodel_from_file(
    os.path.join(os.path.dirname(__file__), '../../grammar/nmodl.tx'))
mm.register_model_processor(scope_processor)


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
