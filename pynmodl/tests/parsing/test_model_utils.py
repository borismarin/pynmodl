import os
from hack import metamodel_with_any_var
from textx.model import children_of_type

import model_utils as mu


#  there's nothing special about 'initial' blocks - any other would do
mm = metamodel_with_any_var(
    os.path.join(os.path.dirname(__file__), '../../grammar/initial.tx'))


def test_utils():
    init = mm.model_from_str('''
    INITIAL {
        x0 = 1
        x1 = x
        x2 = 1 + 1
        x3 = 1 + 1 / x2
        x4 = sin(0)
    }
    ''')
    x0, x1, x2, x3, x4 = init.b.stmts

    assert mu.is_assignment(x0)
    assert mu.is_assignment(x2)
    assert mu.is_assignment(x4)

    assert not mu.is_composite(x0.expression)
    assert not mu.is_composite(x1.expression)
    assert mu.is_composite(x2.expression)
    assert mu.is_composite(x3.expression)
    assert mu.is_composite(x4.expression)

