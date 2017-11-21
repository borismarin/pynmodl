import pytest
from textwrap import dedent
from pynmodl.unparser import Unparser
import re

unp = Unparser().compile


def infun(s):
    return unp('FUNCTION f(x){{{}}}'.format(s))


def compstmt(s):
    inner = re.match('FUNCTION f\(x\)\{(.*)\}', infun(s), re.DOTALL).group(1)
    return dedent(inner[1:-1])


def test_stmt():
    assert compstmt('LOCAL a a = 10') == 'LOCAL a\na = 10'


def test_naming():
    assert compstmt('LOCAL ifa, elseb') == 'LOCAL ifa, elseb'


def test_pow():
    assert compstmt('1^(2 * 3)') == '1 ^ (2 * 3)'


def test_pow_associ():
    assert compstmt('1^2^3') == '1 ^ 2 ^ 3'


def test_if():
    assert(compstmt('if(abs(-1)==1){tan(3.1415926/4)} else{log(-1)}') ==
           dedent('''\
           if(abs(-1) == 1){
               tan(3.1415926 / 4)
           }else{
               log(-1)
           }'''))


def test_logical():
    assert compstmt('2>1 && 2>=1.0e0') == '2 > 1 && 2 >= 1.0e0'


@pytest.mark.skip(reason="TODO!")
def test_funcdef_units():
    print(unp('''
    FUNCTION funfun(x(mV), g(mS))(/ms){
         funfun = x * g
    }
    '''))


@pytest.mark.skip(reason="TODO!")
def test_literal_unit():
    assert compstmt('LOCAL t, c  t=3^(c/(10 (degC)))') == dedent('''
    LOCAL t, c
    t = 3 ^ (c / (10 (degC) )
    ''')
