import pytest
from pynmodl.lems import LemsCompTypeGenerator
from xmlcomp import xml_compare


def test_dx_func():
    lems = '''
    <ComponentType>
      <Exposure name="x" dimension="none"/>
      <Requirement name="v" dimension="none"/>
      <Dynamics>
        <StateVariable name="x" dimension="none"/>
        <DerivedVariable name="f_3" value="2 * 3"/>
        <TimeDerivative value="sin(f_3)" variable="x"/>
      </Dynamics>
    </ComponentType>
    '''

    mod = LemsCompTypeGenerator().compile_to_string('''
        PARAMETER { v }
        STATE { x }
        FUNCTION f(a){f=2*a}
        DERIVATIVE dx {x' = sin(f(3))}
    ''')

    assert(xml_compare(mod, lems))


@pytest.mark.skip(reason="IN PROGRESS!")
def test_v_scoping():
    lems = '''
    <ComponentType>
      <Exposure name="x" dimension="none"/>
      <Requirement name="v" dimension="none"/>
      <Dynamics>
        <StateVariable name="x" dimension="none"/>
        <DerivedVariable name="f_x" value="- x"/>
        <TimeDerivative value="f_x + v" variable="x"/>
      </Dynamics>
    </ComponentType>
    '''

    mod = LemsCompTypeGenerator().compile_to_string('''
        PARAMETER { v }
        STATE { x }
        FUNCTION f(v){f=-v}
        DERIVATIVE dx {x' = f(x) + v}
    ''')

    assert(xml_compare(mod, lems))


def test_blocks():
    lems = '''
        <ComponentType>
          <Exposure name="x" dimension="none"/>
          <Requirement name="v" dimension="none"/>
          <Dynamics>
             <StateVariable name="x" dimension="none"/>
             <ConditionalDerivedVariable name="f_v__b">
               <Case condition="v .neq. 0" value="v"/>
               <Case value="1 * v"/>
             </ConditionalDerivedVariable>
             <DerivedVariable name="f_v" value="2 * f_v__b"/>
             <ConditionalDerivedVariable name="f_4__b">
               <Case condition="4 .neq. 0" value="4"/>
               <Case value="1 * 4"/>
             </ConditionalDerivedVariable>
             <DerivedVariable name="f_4" value="2 * f_4__b"/>
             <TimeDerivative value="log(2) + f_v + f_4 - f_4" variable="x"/>
          </Dynamics>
        </ComponentType>
    '''
    # TODO: test expr in func arguments

    mod = LemsCompTypeGenerator().compile_to_string('''
        PARAMETER {
            v(mV)
        }
        STATE { x }
        FUNCTION f(a){
            LOCAL b
            if(a!=0){
                b=a
            } else{
                b=1*a
            }
            f = 2 * b
        }
        DERIVATIVE dx {x' = log(2) + f(v) + f(4) - f(4) }
    ''')
    assert(xml_compare(mod, lems))

def test_double_funccall():
    lems = '''
        <ComponentType>
          <Exposure name="x" dimension="none"/>
          <Requirement name="v" dimension="none"/>
          <Dynamics>
             <StateVariable name="x" dimension="none"/>
             <ConditionalDerivedVariable name="f_v__b">
               <Case condition="v .neq. 0" value="v"/>
               <Case value="1 * v"/>
             </ConditionalDerivedVariable>
             <DerivedVariable name="f_v" value="2 * f_v__b"/>
             <ConditionalDerivedVariable name="f_4__b">
               <Case condition="4 .neq. 0" value="4"/>
               <Case value="1 * 4"/>
             </ConditionalDerivedVariable>
             <DerivedVariable name="f_4" value="2 * f_4__b"/>
             <TimeDerivative value="f_v + f_v - f_4" variable="x"/>
          </Dynamics>
        </ComponentType>
    '''

    mod = LemsCompTypeGenerator().compile_to_string('''
        PARAMETER {
            v(mV)
        }
        STATE { x }
        FUNCTION f(a){
            LOCAL b
            if(a!=0){
                b=a
            } else{
                b=1*a
            }
            f = 2 * b
        }
        DERIVATIVE dx {x' = f(v) + f(v) - f(4)}
    ''')
    assert(xml_compare(mod, lems))


def test_if():
    lems = '''
    <ComponentType>
      <Exposure name="n" dimension="none"/>
      <Requirement name="v" dimension="none"/>
      <Dynamics>
        <StateVariable name="n" dimension="none"/>
        <DerivedVariable name="alpha_v__x" value="(v + 55) / 10"/>
        <ConditionalDerivedVariable name="alpha_v">
          <Case condition="fabs(alpha_v__x) .gt. 1e-6"
                value="0.1 * alpha_v__x / (1 - exp( - alpha_v__x))"/>
          <Case value="0.1 / (1 - 0.5 * alpha_v__x)"/>
        </ConditionalDerivedVariable>
        <TimeDerivative variable="n" value="alpha_v"/>
      </Dynamics>
    </ComponentType>'''

    mod = LemsCompTypeGenerator().compile_to_string("""
    PARAMETER {
        v (mV)
    }
    STATE { n }
    FUNCTION alpha(Vm)(/ms){
        LOCAL x
        x = (Vm + 55) / 10
        if(fabs(x) > 1e-6){
               alpha=0.1*x/(1-exp(-x))
        }else{
               alpha=0.1/(1-0.5*x)
        }
    }
    DERIVATIVE dn { n' = alpha(v)}
    """)
    assert(xml_compare(mod, lems))


def test_after_if():
    lems = '''
    <ComponentType>
      <Exposure name="n" dimension="none"/>
      <Requirement name="v" dimension="none"/>
      <Dynamics>
        <StateVariable name="n" dimension="none"/>
        <DerivedVariable name="alpha_v__x" value="(v + 55) / 10"/>
        <ConditionalDerivedVariable name="alpha_v">
          <Case condition="fabs(alpha_v__x) .gt. 1e-6"
                value="0.1 * alpha_v__x / (1 - exp( - alpha_v__x))"/>
          <Case value="0.1 / (1 - 0.5 * alpha_v__x)"/>
        </ConditionalDerivedVariable>
        <TimeDerivative variable="n" value="alpha_v"/>
      </Dynamics>
    </ComponentType>'''

    mod = LemsCompTypeGenerator().compile_to_string("""
    PARAMETER {
        v (mV)
    }
    DERIVATIVE dn { n' = alpha(v)}
    FUNCTION alpha(Vm)(/ms){
        LOCAL x
        x = (Vm + 55) / 10
        if(fabs(x) > 1e-6){
               alpha=0.1*x/(1-exp(-x))
        }else{
               alpha=0.1/(1-0.5*x)
        }
    }
    STATE { n }
    """)
    assert(xml_compare(mod, lems))


def test_if_inner_asgn():
    lems = '''
    <ComponentType>
      <Exposure name="n" dimension="none"/>
      <Requirement name="v" dimension="none"/>
      <Dynamics>
        <StateVariable name="n" dimension="none"/>
        <DerivedVariable name="alpha_v__x" value="(v + 55) / 10"/>
        <DerivedVariable name="alpha_v__z" value="0.1 * alpha_v__x / (1 - exp( - alpha_v__x))"/>
        <DerivedVariable name="alpha_v__w" value="0.1 / (1 - 0.5 * alpha_v__x)"/>
        <ConditionalDerivedVariable name="alpha_v">
          <Case condition="fabs(alpha_v__x) .gt. 1e-6"
                value="alpha_v__z"/>
          <Case value="alpha_v__w"/>
        </ConditionalDerivedVariable>
        <TimeDerivative variable="n" value="alpha_v"/>
      </Dynamics>
    </ComponentType>'''

    mod = LemsCompTypeGenerator().compile_to_string("""
    PARAMETER {
        v (mV)
    }
    STATE { n }
    FUNCTION alpha(Vm)(/ms){
        LOCAL x
        LOCAL z,w
        x = (Vm + 55) / 10
        if(fabs(x) > 1e-6){
               z = 0.1*x/(1-exp(-x))
               alpha=z
        }else{
               w = 0.1/(1-0.5*x)
               alpha= w
        }
    }
    DERIVATIVE dn { n' = alpha(v)}
    """)
    assert(xml_compare(mod, lems))

@pytest.mark.skip(reason="IN PROGRESS!")
def test_nested_funccall():
    lems = '''
    <ComponentType>
      <Exposure name="n" dimension="none"/>
      <Requirement name="v" dimension="none"/>
      <Dynamics>
        <StateVariable name="n" dimension="none"/>
        <DerivedVariable name="alpha_v__x" value="(v + 55) / 10"/>
        <ConditionalDerivedVariable name="aphla_alpha_v__x">
          <Case condition="fabs(alpha_v__x) .gt. 1e-6"
                value="0.1 * alpha_v__x / (1 - exp(- alpha_v__x))"/>
          <Case value="0.1 / (1 - 0.5 * alpha_v__x)"/>
        </ConditionalDerivedVariable>
        <DerivedVariable name="alpha_v" value="aphla_alpha_v__x"/>
        <TimeDerivative variable="n" value="alpha_v"/>
      </Dynamics>
    </ComponentType>'''

    mod = LemsCompTypeGenerator().compile_to_string("""
    PARAMETER {
        v (mV)
    }
    STATE { n }
    FUNCTION alpha(Vm)(/ms){
        LOCAL x
        x = (Vm + 55) / 10
        alpha = ahpla(x)
    }
    FUNCTION ahpla(x){
        if(fabs(x) > 1e-6){
               ahpla=0.1*x/(1-exp(-x))
        }else{
               ahpla=0.1/(1-0.5*x)
        }
    }
    DERIVATIVE dn { n' = alpha(v)}
    """)
    assert(xml_compare(mod, lems))


@pytest.mark.skip(reason="IN PROGRESS!")
def test_expr_in_funccall():
    lems = '''
    <ComponentType>
      <Exposure name="n" dimension="none"/>
      <Requirement name="v" dimension="none"/>
      <Dynamics>
        <StateVariable name="n" dimension="none"/>
        <DerivedVariable name="_x0" value="(v + 55) / 10"/>
        <ConditionalDerivedVariable name="alpha_x0">
          <Case condition="fabs(_x0) .gt. 1e-6"
                value="0.1 * _x0 / (1 - exp( - _x0))"/>
          <Case value="0.1 / (1 - 0.5 * _x0)"/>
        </ConditionalDerivedVariable>
        <TimeDerivative variable="n" value="alpha_args0"/>
      </Dynamics>
    </ComponentType>'''
    mod = LemsCompTypeGenerator().compile_to_string("""
    PARAMETER {
        v (mV)
    }
    STATE { n }
    FUNCTION alpha(x)(/ms){
        if(fabs(x) > 1e-6){
               alpha=0.1*x/(1-exp(-x))
        }else{
               alpha=0.1/(1-0.5*x)
        }
    }
    DERIVATIVE dn { n' = alpha((v + 55)/10)}
    """)
    assert(xml_compare(mod, lems))
