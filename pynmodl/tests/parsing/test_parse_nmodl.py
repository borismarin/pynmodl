import os
from textx.metamodel import metamodel_from_file

mm = metamodel_from_file(
    os.path.join(os.path.dirname(__file__), '../../grammar/nmodl.tx'))


def test_neuron():
    p = """
        TITLE adapted from an oldschool modfile bundled with nrn
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
            USEION na READ ena WRITE ina
            RANGE gnabar, gkbar, gl, el
            NONSPECIFIC_CURRENT il
        }

        PARAMETER {
            v (mV)
            celsius = 6.3 (degC)
            dt (ms)
            gnabar = .12 (mho/cm2)
            ena = 50 (mV)
            gkbar = .036 (mho/cm2)
            ek = -77.5 (mV)
            gl = .0003 (mho/cm2)
            el = -54.3 (mV)
        }

        STATE {
            m h n
        }

        ASSIGNED {
            ina (mA/cm2)
            ik (mA/cm2)
            il (mA/cm2)
            minf hinf ninf mexp hexp nexp
        }

        BREAKPOINT {
            SOLVE states
            ina = gnabar*m*m*m*h*(v - ena)
            ik = gkbar*n*n*n*n*(v - ek)
            il = gl*(v - el)
        }

        UNITSOFF

        INITIAL {
            rates(v)
            m = minf
            h = hinf
            n = ninf
        }

        PROCEDURE states() {  :Computes state variables m, h, and n
           rates(v)      :             at the current v and dt.
           m = m + mexp*(minf-m)
           h = h + hexp*(hinf-h)
           n = n + nexp*(ninf-n)
        }
        PROCEDURE rates(v) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
            LOCAL  q10, tinc, alpha, beta, sum
            TABLE minf, mexp, hinf, hexp, ninf, nexp DEPEND dt, celsius FROM -100 TO 100 WITH 200
            q10 = 3^((celsius - 6.3)/10)
            tinc = -dt * q10
                    :"m" sodium activation system
            alpha = .1 * vtrap(-(v+40),10)
            beta =  4 * exp(-(v+65)/18)
            sum = alpha + beta
            minf = alpha/sum
            mexp = 1 - exp(tinc*sum)
                    :"h" sodium inactivation system
            alpha = .07 * exp(-(v+65)/20)
            beta = 1 / (exp(-(v+35)/10) + 1)
            sum = alpha + beta
            hinf = alpha/sum
            hexp = 1 - exp(tinc*sum)
                    :"n" potassium activation system
            alpha = .01*vtrap(-(v+55),10)
            beta = .125*exp(-(v+65)/80)
            sum = alpha + beta
            ninf = alpha/sum
            nexp = 1 - exp(tinc*sum)
        }

        FUNCTION vtrap(x,y) {  :Traps for 0 in denominator of rate eqns.
            if (fabs(x/y) < 1e-6) {
                    vtrap = y*(1 - x/y/2)
            }else{
                    vtrap = x/(exp(x/y) - 1)
            }
        }
        """
    prog = mm.model_from_str(p)

    s, g, ui_k, ui_na, r, n = prog.neuron.statements
    assert([gg.name for gg in g.globals] == ['minf', 'hinf', 'ninf', 'mexp', 'hexp', 'nexp'])
    assert(s.suffix == 'hh1')
    assert([r.name for r in ui_k.r.reads] == ['ek'])
    assert([w.name for w in ui_na.w.writes] == ['ina'])
    assert(ui_k.v.valence == 1)

    assert([sv.name for sv in prog.state.state_vars] == ['m', 'h', 'n'])

    assert(prog.units.unit_defs[0].base_unit == '(millivolt)')

    p0 = prog.parameter.parameters[0]
    assert(p0.name == 'v')
    assert(p0.unit == '(mV)')

    solve = prog.breakpoint.statements[0]
    assert solve.solve.name == 'states' # this is the actual PROCEDURE

    states, rates, vtrap = prog.functions_procedures.fd
    assert(rates.b.stmts[1].tabbed[0].name == 'minf')

