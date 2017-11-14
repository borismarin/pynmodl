COMMENT

Potassium current for the soma
 

ENDCOMMENT
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
}
 
NEURON {
        SUFFIX Kaxon
        USEION k READ ek WRITE ik
        RANGE gkaxon, ik
        GLOBAL ninf, nexp, ntau
}
 
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
 
PARAMETER {
        v (mV)
        celsius = 24 (degC)
        dt (ms)
        gkaxon = .0319 (mho/cm2)
        ek = -100 (mV)
}
 
STATE {
        n 
}
 
ASSIGNED {
        ik (mA/cm2)
        ninf 
	nexp 
	ntau (ms)
}
 
INITIAL {
	n = ninf
}

BREAKPOINT {
        SOLVE states
	ik = gkaxon*n*n*n*n*(v - ek)    
}

PROCEDURE states() {	:exact when v held constant
	evaluate_fct(v)
	n = n + nexp*(ninf - n)
	VERBATIM
	return 0;
	ENDVERBATIM 
}
UNITSOFF
PROCEDURE evaluate_fct(v(mV)) {  :Computes rate and other constants at 
		      :current v.
                      :Call once from HOC to initialize inf at resting v.
        LOCAL q10, tinc, alpha, beta
        TABLE ninf, nexp, ntau DEPEND dt, celsius FROM -200 TO 
100 WITH 300
:		q10 = 3^((celsius - 24)/10)
		q10 = 1	: BPG
		tinc = -dt*q10
		alpha = 0.018*vtrap(-(v-25),25)
		beta = 0.0036*vtrap(v-35,12)
		ntau = 1/(alpha + beta)
		ninf = alpha*ntau
		nexp = 1-Exp(tinc/ntau)
}
FUNCTION vtrap(x,y) {	:Traps for 0 in denominator of rate eqns.
		if (fabs(x/y) < 1e-6) {
			vtrap = y*(1 - x/y/2)
		}else{
			vtrap = x/(Exp(x/y) - 1)
		}
}
FUNCTION Exp(x) {
		if (x < -100) {
			Exp = 0
		}else{
			Exp = exp(x)
		}
}
UNITSON
