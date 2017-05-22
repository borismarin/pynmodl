import os
from hack import metamodel_with_any_var
from textx.model import children_of_type

mm = metamodel_with_any_var(
    os.path.join(os.path.dirname(__file__), '../../grammar/derivative.tx'))

def test_derivative():
    nrn = """
    DERIVATIVE states {
        trates(v+vshift)
        m' =  (minf-m)/mtau
        h' =  (hinf-h)/htau
        }
    """
    deriv = mm.model_from_str(nrn)
    assert(deriv.name == 'states')
    expr, mprime, hprime = deriv.b.stmts
    fcall = children_of_type('FuncCall', expr)[0]
    assert(fcall.func.user.name == 'trates')
    assert(mprime.variable == 'm')


