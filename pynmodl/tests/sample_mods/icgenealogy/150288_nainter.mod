: spike-generating sodium channel (interneuron)

NEURON {
	SUFFIX nainter
	USEION na READ ena WRITE ina
	RANGE gnabar, ina, gnaer
	RANGE minf, hinf, mtau, htau
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}

PARAMETER {
	v (mV)
	dt (ms)
	gnabar = 0.035 (mho/cm2) <0,1e9>
	ena = 45 (mV)
}

STATE {
	m h
}

ASSIGNED {
	ina (mA/cm2)
	minf hinf 
	mtau (ms)
	htau (ms)
	gna (mho/cm2)
}

INITIAL {
	rate(v)
	m = minf
	h = hinf
}

BREAKPOINT {
	SOLVE states METHOD cnexp
	gna = gnabar*m*m*m*h
	ina = gna*(v-ena)
}

DERIVATIVE states {
	rate(v)
	m' = (minf-m)/mtau
	h' = (hinf-h)/htau
}

UNITSOFF

FUNCTION malf(v(mV)) {
	malf = 2.1*exp((v+18.5)/11.75)   :malf = 2.1*exp((v+18.5)/11.57)
}

FUNCTION mbet(v(mV)) {
	mbet = 2.1*exp(-(v+18.5)/27)
}	

FUNCTION half(v(mV)) {
	half = 0.045*exp(-(v+29)/33)
}

FUNCTION hbet(v(mV)) {
	hbet = 0.045*exp((v+29)/12.2)
}

PROCEDURE rate(v(mV)) { LOCAL msum, hsum, ma, mb, ha, hb

	ma = malf(v) mb = mbet(v) ha = half(v) hb = hbet(v)
	
	msum = ma+mb
	minf = ma/msum
	mtau = 1/(msum)
	
	hsum = ha+hb
	hinf = ha/hsum
	htau = 1/(hsum)
}

UNITSON