from textwrap import dedent
from pynmodl.unparser import Unparser

unp = Unparser().compile


def test_nmodl():
    src = dedent('''\
    TITLE gsquid.mod   squid sodium, potassium, and leak channels
    UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
        F = (faraday)(coulomb)
    }
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
        celsius = 6.3 (degC)
        dt (ms)
        gnabar = 0.12 (mho/cm2)
        ena = 50 (mV)
        gkbar = 0.036 (mho/cm2)
        ek = -77.5 (mV)
        gl = 0.0003 (mho/cm2)
        el = -54.3 (mV)
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
    }
    STATE {
        m
        h
        n
    }
    INITIAL {
        rates(v)
        m = minf
        h = hinf
        n = ninf
    }
    BREAKPOINT {
        SOLVE states METHOD sparse
        ina = gnabar * m * m * m * h * (v - ena)
        ik = gkbar * n * n * n * n * (v - ek)
        il = gl * (v - el)
    }
    DERIVATIVE states {
        rates(v)
        m = m + mexp * (minf - m)
        h = h + hexp * (hinf - h)
        n = n + nexp * (ninf - n)
    }
    PROCEDURE rates(v){
        LOCAL q10, tinc, alpha, beta, sum
        TABLE minf, mexp, hinf, hexp, ninf, nexp DEPEND dt, celsius FROM -100 TO 100 WITH 200
        q10 = 3 ^ ((celsius - 6.3) / 10)
        tinc = -dt * q10
        alpha = 0.1 * vtrap(-(v + 40), 10)
        beta = 4 * exp(-(v + 65) / 18)
        sum = alpha + beta
        minf = alpha / sum
        mexp = 1 - exp(tinc * sum)
        alpha = 0.07 * exp(-(v + 65) / 20)
        beta = 1 / (exp(-(v + 35) / 10) + 1)
        sum = alpha + beta
        hinf = alpha / sum
        hexp = 1 - exp(tinc * sum)
        alpha = 0.01 * vtrap(-(v + 55), 10)
        beta = 0.125 * exp(-(v + 65) / 80)
        sum = alpha + beta
        ninf = alpha / sum
        nexp = 1 - exp(tinc * sum)
    }
    FUNCTION vtrap(x, y){
        if(fabs(x / y) < 1e-6){
            vtrap = y * (1 - x / y / 2)
        }else{
            vtrap = x / (exp(x / y) - 1)
        }
    }''')
    assert unp(src) == src
