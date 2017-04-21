import os
from textx.metamodel import metamodel_from_file

mm = metamodel_from_file(
    os.path.join(os.path.dirname(__file__), '../nmodl.tx'))


def test_neuron():
    from textwrap import dedent
    p = dedent("""
        TITLE test!
        UNITS {
            (mV) = (millivolt)
        }
        COMMENT
            time flies like an arrow
            fruit flies like a banana
            ENDCOMMENT
        NEURON {
            SUFFIX hh1   : comment!
            GLOBAL minf, hinf, ninf, mexp, hexp, nexp
            USEION k WRITE ik READ ek VALENCE +1
            RANGE gnabar, gkbar, gl, el
            NONSPECIFIC_CURRENT il
            }
        PARAMETER {
            ek (mV)  :typically~-77.5
        }
        STATE{ m h }
        """)
    prog = mm.model_from_str(p)

    s, g, u, r, n = prog.neuron.statements
    assert(g.globals == ['minf', 'hinf', 'ninf', 'mexp', 'hexp', 'nexp'])
    assert(s.suffix == 'hh1')
    assert((u.r.reads, u.w.writes, u.v.valence) == (['ek'], ['ik'], 1))

    assert(prog.state.state_vars == ['m', 'h'])

    assert(prog.units.unit_defs[0].base_unit == '(millivolt)')

    p0 = prog.parameter.parameters[0]
    assert(p0.name == 'ek')
    assert(p0.unit == '(mV)')
