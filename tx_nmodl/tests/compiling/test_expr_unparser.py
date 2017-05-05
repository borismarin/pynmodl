import pytest
from textwrap import dedent
from tx_nmodl.expr_unparser import Unparser

unp = Unparser().compile


def test_stmt():
    assert(unp('{LOCAL a a = 10}') == '{LOCAL a\na = 10}')


def test_pow():
    assert(unp('1^(2 * 3)') == ('1 ^ (2 * 3)'))


def test_pow_associ():
    assert(unp('1^2^3') == '1 ^ 2 ^ 3')


def test_if():
    assert(unp('if(abs(-1)==1){tan(3.1415926/4)}\n else{log(-1)}') ==
           dedent('''\
           if(abs(-1) == 1)
           {tan(3.1415926 / 4)}
           else
           {log(-1)}'''))


def test_logical():
    assert(unp('2>1 && 2>=1.0e0') == '2 > 1 && 2 >= 1.0e0')


@pytest.mark.skip(reason="TODO!")
def test_funcdef_units():
    f = dedent('''
    FUNCTION funfun(x(mV), g(mS))(/ms){
         funfun = x * g
    }
    ''')


@pytest.mark.skip(reason="TODO!")
def test_literal_unit():
    s = 'tadj = q10^((celsius - temp)/(10 (degC)))'
