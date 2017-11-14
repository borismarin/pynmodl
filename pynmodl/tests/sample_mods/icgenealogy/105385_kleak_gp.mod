NEURON {
	SUFFIX kleak_gp
	USEION k READ ek WRITE ik
	RANGE ik, e, g, gbar
}

UNITS {
	(mV) = (millivolt)
	(mA) = (milliamp)
	(S) = (siemens)
}

PARAMETER {
	gbar = 1	(S/cm2)
}

ASSIGNED {
	g	(S/cm2)
	ik	(mA/cm2)
	v	(mV)
	ek	(mV)
}

BREAKPOINT {
	g = gbar
	ik = g*(v-ek)
}