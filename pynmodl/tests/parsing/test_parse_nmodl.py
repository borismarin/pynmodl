import os
from textx.metamodel import metamodel_from_file
from textx.model import children_of_type

mm = metamodel_from_file(
    os.path.join(os.path.dirname(__file__), '../../grammar/nmodl.tx'))


def test_full_nmodl():
    p = """
        TITLE adapted from an oldschool modfile bundled with nrn
        UNITS {
            (mV) = (millivolt)
            (mS) = (millisiemens)
            F = (faraday) (coulomb)
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

        INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

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
            m h n z<1e-4>
            w[2]
        }

        ASSIGNED {
            ina (mA/cm2)
            ik (mA/cm2)
            il (mA/cm2)
            minf hinf ninf mexp hexp nexp
            x[3]
        }

        BREAKPOINT {
            SOLVE states
            ina = gnabar*m*m*m*h*(v - ena)
            ik = gkbar*n*n*n*n*(v - ek)
            il = gl*(v - el)
            x[0] = 1
            x[1+1] = x[0] + 2
        }

        UNITSOFF

        INITIAL {
            LOCAL j
            rates(v)
            m = minf
            h = hinf
            n = ninf
            FROM j = 0 TO 1/1 {
                w[j] = 0
            }
        }

        PROCEDURE states() {  :Computes state variables m, h, and n
           rates(v)      :             at the current v and dt.
           m = m + mexp*(minf-m)
           h = h + hexp*(hinf-h)
           n = n + nexp*(ninf-n)
           LOCAL i[2]
           i[0] = 0
           i[1] = 1
           w[i[0]] = w[0] + dt * w[i[1]]
           w[1] = w[1] - dt * w[0]
        }
        PROCEDURE rates(v) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
            LOCAL  q10, tinc, alpha, beta, sum, tenF
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
            tenF = F * 10 
        }
        VERBATIM
            printf("fruit flies like a banana");
        ENDVERBATIM

        FUNCTION vtrap(x,y) {  :Traps for 0 in denominator of rate eqns.
            if (fabs(x/y) < 1e-6) {
                    vtrap = y*(1 - x/y/2)
                    }
            else if (2 < 1) {
                : bang!!!
            }
            else if ( 3 == 2 ) {
                : bang again!!!
            }
            else{
                    vtrap = x/(exp(x/y) - 1)
            }
            VERBATIM
                printf("fruit flies like a banana");
            ENDVERBATIM
        }
        """
    blocks = mm.model_from_str(p).blocks
    (title, units, neuron, indep, parameter, state, assigned, breakpoint,
     _, init) = blocks[:10]

    s, g, ui_k, ui_na, r, n = neuron.statements
    assert([gg.name for gg in g.globals] ==
           ['minf', 'hinf', 'ninf', 'mexp', 'hexp', 'nexp'])
    assert(s.suffix == 'hh1')
    assert([r.name for r in ui_k.r[0].reads] == ['ek'])
    assert([w.name for w in ui_na.w[0].writes] == ['ina'])
    assert(ui_k.v[0].valence == 1)

    assert([sv.name for sv in state.state_vars] == ['m', 'h', 'n', 'z', 'w'])
    w = state.state_vars[-1]
    assert w.len == 2

    assert(units.unit_defs[0].base_units[0] == '(millivolt)')

    assert(indep.name == 't')

    p0 = parameter.parameters[0]
    assert(p0.name == 'v')
    assert(p0.unit == '(mV)')

    solve = breakpoint.b.stmts[0]
    assert solve.solve.name == 'states'  # this is the actual PROCEDURE

    states, rates, vtrap = blocks[-3:]
    assert(rates.b.stmts[1].tabbed[0].var.name == 'minf')
    w_update = states.b.stmts[-1]

    assert w_update.variable.var.name == 'w'
    assert children_of_type('Num', w_update.variable.idx)[0].num == '1'

    from_to = init.b.stmts[-1]
    assert from_to.counter.name == 'j'

    vtrap = blocks[-1]
    assert len(vtrap.b.stmts[0].elif_blk) == 2
    assert len(vtrap.b.stmts[0].elif_cond) == 2
