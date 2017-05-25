from textwrap import dedent
from pynmodl.unparser import Unparser

unp = Unparser().compile


def test_neuron():
    src = dedent('''\
    NEURON {
        SUFFIX hh1
        USEION na READ ena WRITE ina
        USEION k READ ek WRITE ik VALENCE +1
        NONSPECIFIC_CURRENT il
        RANGE gnabar, gkbar, gl, el
        GLOBAL minf, hinf, ninf, mexp, hexp, nexp
    }
    PARAMETER {
        v (mV)
        gnabar = 0.12 (mho/cm2)
        ena = 50 (mV)
        gkbar = 0.036 (mho/cm2)
        ek = -77.5 (mV)
        gl = 0.0003 (mho/cm2)
        el = -54.3 (mV)
    }
    UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
    }
    ASSIGNED {
        ina (mA/cm2)
        ik (mA/cm2)
        il (mA/cm2)
        minf
        hinf
        ninf
        mexp
        hexp
        nexp
    }''')
    assert unp(src) == src
