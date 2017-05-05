import os
from textx.metamodel import metamodel_from_file

mm = metamodel_from_file(
    os.path.join(os.path.dirname(__file__), '../nmodl.tx'))


def test_neuron():
    p = """
        TITLE test!
        UNITS {
            (mV) = (millivolt)
            (mS) = (millisiemens)
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
        ASSIGNED{
            minf hinf ninf mexp hexp nexp
            ik
        }

        PARAMETER {
            ek (mV)  :typically~-77.5
            gnabar (mS)
            gkbar (mS)
            gl (mS)
            el (mV)
        }
        STATE{ m h }
        """
    prog = mm.model_from_str(p)

    s, g, u, r, n = prog.neuron.statements
    assert([gg.name for gg in g.globals] == ['minf', 'hinf', 'ninf', 'mexp', 'hexp', 'nexp'])
    assert(s.suffix == 'hh1')
    assert([r.name for r in u.r.reads] == ['ek'])
    assert([w.name for w in u.w.writes] == ['ik'])
    assert(u.v.valence == 1)

    assert([sv.name for sv in prog.state.state_vars] == ['m', 'h'])

    assert(prog.units.unit_defs[0].base_unit == '(millivolt)')

    p0 = prog.parameter.parameters[0]
    assert(p0.name == 'ek')
    assert(p0.unit == '(mV)')
