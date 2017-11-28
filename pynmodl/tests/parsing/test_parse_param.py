import os
from textx.metamodel import metamodel_from_file

mm = metamodel_from_file(
    os.path.join(os.path.dirname(__file__), '../../grammar/parameter.tx'))


def test_neuron():
    from textwrap import dedent
    p = dedent("""
    PARAMETER {
     v (mV)
     celsius = 6.3 (degC)
     erev = -70      (mV) <-1e2, 0.1e3>
    }
    """)
    pars = mm.model_from_str(p).parameters
    assert(pars[0].name == 'v')
    assert(pars[1].unit == '(degC)')
    assert(float(pars[2].ulim) == 0.1e3)


