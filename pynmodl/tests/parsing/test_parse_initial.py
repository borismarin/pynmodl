import os
from hack import metamodel_with_any_var
from textx.model import children_of_type

mm = metamodel_with_any_var(
    os.path.join(os.path.dirname(__file__), '../../grammar/initial.tx'))

def test_initial():
    nrn ='''
    INITIAL {
        tadj = q10^((celsius - temp)/(10 (degC))) 

        trates(v+vshift)
        m = minf
        h = hinf
        SOLVE ks STEADYSTATE sparse
    }
    '''
    init = mm.model_from_str(nrn)
    tadk, proc, m0, h0, solve = init.b.stmts
    fcall = children_of_type('FuncCall', proc)[0]
    assert(fcall.func.user.name == 'trates')
    assert(children_of_type('VarRef', h0.expression)[0].var.name == 'hinf')


