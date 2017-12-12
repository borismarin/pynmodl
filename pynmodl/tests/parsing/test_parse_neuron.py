import os
from textx.metamodel import metamodel_from_file
from hack import metamodel_with_any_var

mm = metamodel_with_any_var(
    os.path.join(os.path.dirname(__file__), '../../grammar/neuron.tx'))


def test_neuron():
    from textwrap import dedent
    nrn = dedent("""
    NEURON {
        SUFFIX hh1   : comment!
        GLOBAL minf, hinf
        USEION k WRITE ik READ ek VALENCE +1
        RANGE gnabar, gkbar
        NONSPECIFIC_CURRENT il
    }
    """)
    s, g, u, r, n = mm.model_from_str(nrn).statements
    assert([gg.name for gg in g.globals] == ['minf', 'hinf'])
    assert(s.suffix == 'hh1')
    assert([r.name for r in u.r[0].reads] == ['ek'])
    assert([w.name for w in u.w[0].writes] == ['ik'])
    assert(u.v[0].valence == 1)


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
    assert([g.name for g in g1.globals] == ['a', 'b'])
    assert([g.name for g in g2.globals] == ['x', 'y'])
    assert(s.suffix == 'suf')
