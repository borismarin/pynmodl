import os
from hack import metamodel_with_any_var
from textx.model import children_of_type


mm = metamodel_with_any_var(
    os.path.join(os.path.dirname(__file__), '../../grammar/solvable_block.tx'))


def test_solvableblock():
    s = """
    {
        SOLVE states
        ina = gnabar*m*h*(v - ena)
        ik = gkbar*n*(v - ek)
        il = gl*(v - el)
    }
    """
    block = mm.model_from_str(s)
    solve, ina, ik, il = block.stmts
    assert solve.solve.name == 'states'
    assert children_of_type('VarRef', ina)[0].var.name == 'ina'
