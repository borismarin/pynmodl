import os
from hack import metamodel_with_any_var
from textx.model import children_of_type


mm = metamodel_with_any_var(
    os.path.join(os.path.dirname(__file__), '../../grammar/kinetic.tx'))


def test_kinetic():
    s = """
    KINETIC kin {
    rates(v)
    ~ c1 <-> c2 (kf1, kb1)
    ~ c2 <-> o (kf2, kb2)
    CONSERVE c1 + c2 + o = 1
    }
    """
    kinetic = mm.model_from_str(s)
    rates, react1, react2, conserve = kinetic.statements
    assert kinetic.name == 'kin'
    assert [op.var.name for op in conserve.reactants.op] == ['c1', 'c2', 'o']
