import os
from textx.metamodel import metamodel_from_file

mm = metamodel_from_file(
    os.path.join(os.path.dirname(__file__), '../neuron.tx'))


def test_neuron():
    from textwrap import dedent
    nrn = dedent("""
    NEURON {
        SUFFIX hh1   : comment!
        GLOBAL minf, hinf, ninf, mexp, hexp, nexp
        USEION k WRITE ik READ ek VALENCE +1
        RANGE gnabar, gkbar, gl, el
        NONSPECIFIC_CURRENT il
    }
    """)
    s, g, u, r, n = mm.model_from_str(nrn).statements
    assert(g.globals == ['minf', 'hinf', 'ninf', 'mexp', 'hexp', 'nexp'])
    assert(s.suffix == 'hh1')
    assert((u.r.reads, u.w.writes, u.v.valence) == (['ek'], ['ik'], 1))


def test_multiple():
    from textwrap import dedent
    nrn = dedent("""
    NEURON {
        COMMENT
        time flies like an arrow
        ENDCOMMENT
        GLOBAL a,b
        SUFFIX suf
        GLOBAL x,y

    }
    """)
    g1, s, g2 = mm.model_from_str(nrn).statements
    assert(g1.globals == ['a', 'b'])
    assert(g2.globals == ['x', 'y'])
    assert(s.suffix == 'suf')
