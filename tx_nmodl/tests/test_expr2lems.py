from textwrap import dedent
from tx_nmodl.expr2lems import Lems

unp = Lems().compile


def test():
    s = dedent('''
    <DerivedVariable name="f_3" value="2 * 3"/>
    <TimeDerivative variable="x" value="sin(f_3 + 1)"/>''')
    assert(unp("{FUNCTION f(a){f=2*a} x' = sin(f(3)+1)}") == s)
