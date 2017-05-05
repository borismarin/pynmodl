from tx_nmodl.expr2lems import Lems
from xmlcomp import xml_compare


def test_dx_func():
    c = Lems()
    s = '''
        <ComponentType>
           <Dynamics>
              <DerivedVariable name="f_3" value="2 * 3"/>
              <TimeDerivative value="sin(f_3)" variable="x"/>
           </Dynamics>
        </ComponentType>
        '''
    assert(xml_compare(c.compile("{FUNCTION f(a){f=2*a} x' = sin(f(3))}"), s))


def test_blocks():
    c = Lems()
    s = '''
        <ComponentType>
           <Dynamics>
              <ConditionalDerivedVariable name="f_3__b">
                <Case condition="3 .neq. 0" value="3"/>
                <Case value="1 * 3"/>
              </ConditionalDerivedVariable>
              <DerivedVariable name="f_3" value="2 * f_3__b"/>
              <ConditionalDerivedVariable name="f_4__b">
                <Case condition="4 .neq. 0" value="4"/>
                <Case value="1 * 4"/>
              </ConditionalDerivedVariable>
              <DerivedVariable name="f_4" value="2 * f_4__b"/>
              <TimeDerivative value="log(2) + f_3 + f_4" variable="x"/>
           </Dynamics>
        </ComponentType>
        '''
    mod = c.compile('''{
    FUNCTION f(a){
        LOCAL b
        if(a!=0){
            b=a
        } else{
            b=1*a
        }
        f = 2 * b
    }
    x' = log(2) + f(3) + f(4)
    }''')
    assert(xml_compare(mod, s))


def test_if():
    c = Lems()
    s = '''
    <ComponentType>
      <Dynamics>
        <DerivedVariable name="alpha_42__x" value="(42 + 55) / 10"/>
        <ConditionalDerivedVariable name="alpha_42">
          <Case condition="fabs(alpha_42__x) .gt. 1e-6"
                value="0.1 * alpha_42__x / (1 - exp( - alpha_42__x))"/>
          <Case value="0.1 / (1 - 0.5 * alpha_42__x)"/>
        </ConditionalDerivedVariable>
        <TimeDerivative variable="n" value="alpha_42"/>
      </Dynamics>
    </ComponentType>'''

    mod = """
    {FUNCTION alpha(Vm){
        LOCAL x
        x = (Vm + 55) / 10
        if(fabs(x) > 1e-6){
               alpha=0.1*x/(1-exp(-x))
        }else{
               alpha=0.1/(1-0.5*x)
        }
    }
    n' = alpha(42)}
    """
    assert(xml_compare(c.compile(mod), s))

def test_after_if():
    c = Lems()
    s = '''
    <ComponentType>
      <Dynamics>
        <DerivedVariable name="alpha_42__x" value="(42 + 55) / 10"/>
        <ConditionalDerivedVariable name="alpha_42">
          <Case condition="fabs(alpha_42__x) .gt. 1e-6"
                value="0.1 * alpha_42__x / (1 - exp( - alpha_42__x))"/>
          <Case value="0.1 / (1 - 0.5 * alpha_42__x)"/>
        </ConditionalDerivedVariable>
        <TimeDerivative variable="n" value="alpha_42"/>
      </Dynamics>
    </ComponentType>'''

    mod = """
    {n' = alpha(42)
    FUNCTION alpha(Vm){
        LOCAL x
        x = (Vm + 55) / 10
        if(fabs(x) > 1e-6){
               alpha=0.1*x/(1-exp(-x))
        }else{
               alpha=0.1/(1-0.5*x)
        }
    }}
    """
    assert(xml_compare(c.compile(mod), s))
