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


def test_v_scoping():
    lems = '''
    <ComponentType>
      <Exposure name="x" dimension="none"/>
      <Requirement name="v" dimension="none"/>
      <Dynamics>
        <StateVariable name="x" dimension="none"/>
        <DerivedVariable name="f_x" value="-x"/>
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
             <ConditionalDerivedVariable name="f_v::b">
               <Case condition="v .neq. 0" value="v"/>
               <Case value="1 * v"/>
             </ConditionalDerivedVariable>
             <DerivedVariable name="f_v" value="2 * f_v::b"/>
             <ConditionalDerivedVariable name="f_4::b">
               <Case condition="4 .neq. 0" value="4"/>
               <Case value="1 * 4"/>
             </ConditionalDerivedVariable>
             <DerivedVariable name="f_4" value="2 * f_4::b"/>
             <TimeDerivative value="log(2) + f_v + f_4 - f_4" variable="x"/>
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
             <ConditionalDerivedVariable name="f_v::b">
               <Case condition="v .neq. 0" value="v"/>
               <Case value="1 * v"/>
             </ConditionalDerivedVariable>
             <DerivedVariable name="f_v" value="2 * f_v::b"/>
             <ConditionalDerivedVariable name="f_4::b">
               <Case condition="4 .neq. 0" value="4"/>
               <Case value="1 * 4"/>
             </ConditionalDerivedVariable>
             <DerivedVariable name="f_4" value="2 * f_4::b"/>
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
        <DerivedVariable name="alpha_v::x" value="(v + 55) / 10"/>
        <ConditionalDerivedVariable name="alpha_v">
          <Case condition="fabs(alpha_v::x) .gt. 1e-6"
                value="0.1 * alpha_v::x / (1 - exp(-alpha_v::x))"/>
          <Case value="0.1 / (1 - 0.5 * alpha_v::x)"/>
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
        <DerivedVariable name="alpha_v::x" value="(v + 55) / 10"/>
        <ConditionalDerivedVariable name="alpha_v">
          <Case condition="fabs(alpha_v::x) .gt. 1e-6"
                value="0.1 * alpha_v::x / (1 - exp(-alpha_v::x))"/>
          <Case value="0.1 / (1 - 0.5 * alpha_v::x)"/>
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
        <DerivedVariable name="alpha_v::x" value="(v + 55) / 10"/>
        <DerivedVariable name="alpha_v::z"
                value="0.1 * alpha_v::x / (1 - exp(-alpha_v::x))"/>
        <DerivedVariable name="alpha_v::w"
                value="0.1 / (1 - 0.5 * alpha_v::x)"/>
        <ConditionalDerivedVariable name="alpha_v">
          <Case condition="fabs(alpha_v::x) .gt. 1e-6"
                value="alpha_v::z"/>
          <Case value="alpha_v::w"/>
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


def test_nested_funccall():
    lems = '''
    <ComponentType>
      <Exposure name="n" dimension="none"/>
      <Requirement name="v" dimension="none"/>
      <Dynamics>
        <StateVariable name="n" dimension="none"/>
        <DerivedVariable name="alpha_v::x" value="(v + 55) / 10"/>
        <ConditionalDerivedVariable name="ahpla_alpha_v::x">
          <Case condition="fabs(alpha_v::x) .gt. 1e-6"
                value="0.1 * alpha_v::x / (1 - exp(-alpha_v::x))"/>
          <Case value="0.1 / (1 - 0.5 * alpha_v::x)"/>
        </ConditionalDerivedVariable>
        <DerivedVariable name="alpha_v" value="ahpla_alpha_v::x"/>
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


def test_expr_in_funccall():
    lems = '''
    <ComponentType>
      <Exposure name="n" dimension="none"/>
      <Requirement name="v" dimension="none"/>
      <Dynamics>
        <StateVariable name="n" dimension="none"/>
        <DerivedVariable name="_aux0" value="(v + 55) / 10"/>
        <ConditionalDerivedVariable name="alpha__aux0">
          <Case condition="fabs(_aux0) .gt. 1e-6"
                value="0.1 * _aux0 / (1 - exp(-_aux0))"/>
          <Case value="0.1 / (1 - 0.5 * _aux0)"/>
        </ConditionalDerivedVariable>
        <TimeDerivative variable="n" value="alpha__aux0"/>
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
    DERIVATIVE dn {
        n' = alpha((v + 55)/10)}
    """)
    assert(xml_compare(mod, lems))


def test_aux_var():
    lems = '''
    <ComponentType>
      <Exposure name="x" dimension="none"/>
      <Requirement name="v" dimension="none"/>
      <Dynamics>
        <StateVariable name="x" dimension="none"/>
        <DerivedVariable name="_aux0" value="-3 * v"/>
        <DerivedVariable name="f__aux0" value="2 * _aux0"/>
        <TimeDerivative value="sin(f__aux0)" variable="x"/>
      </Dynamics>
    </ComponentType>
    '''

    mod = LemsCompTypeGenerator().compile_to_string('''
        PARAMETER { v }
        STATE { x }
        FUNCTION f(a){f=2*a}
        DERIVATIVE dx {x' = sin(f(-3*v))}
    ''')

    assert(xml_compare(mod, lems))


@pytest.mark.skip(reason='IN PROGRESS!')
def test_multiple_call():
    lems = '''
    <ComponentType>
      <Exposure name="n" dimension="none"/>
      <Requirement name="v" dimension="none"/>
      <Dynamics>
        <StateVariable name="n" dimension="none"/>
        <DerivedVariable name="_aux0" value="(v + 55) / 10"/>
        <ConditionalDerivedVariable name="alpha_aux0">
          <Case condition="fabs(_aux1) .gt. 1e-6"
                value="0.1 * _aux0 / (1 - exp(-_aux0))"/>
          <Case value="0.1 / (1 - 0.5 * _aux0)"/>
        </ConditionalDerivedVariable>
        <DerivedVariable name="_aux1" value="_aux0"/>
        <DerivedVariable name="x" value="(v + 55) / 10"/>
        <DerivedVariable name="id_x" value="x"/>
        <DerivedVariable name="_aux0" value="id_x"/>
        <TimeDerivative variable="n" value="alpha_aux0"/>
      </Dynamics>
    </ComponentType>'''
    mod = LemsCompTypeGenerator().compile_to_string("""
    PARAMETER {
        v (mV)
    }
    STATE { n }
    FUNCTION id(x){id = x}
    FUNCTION alpha(x)(/ms){
        if(fabs(id(x)) > 1e-6){
               alpha=0.1*x/(1-exp(-x))
        }else{
               alpha=0.1/(1-0.5*x)
        }
    }
    DERIVATIVE dn {
        LOCAL x
        x = (v + 55)/10
        n' = alpha(id(x))}
    """)
    assert(xml_compare(mod, lems))


@pytest.mark.skip(reason='IN PROGRESS!')
def test_scoping_mangling():
    lems = '''
    <ComponentType>
      <Exposure name="n" dimension="none"/>
      <Requirement name="v" dimension="none"/>
      <Dynamics>
        <StateVariable name="n" dimension="none"/>
        <DerivedVariable name="_aux0" value="(v + 55) / 10"/>
        <ConditionalDerivedVariable name="alpha_aux0">
          <Case condition="fabs(_aux0) .gt. 1e-6"
                value="0.1 * _aux0 / (1 - exp(-_aux0))"/>
          <Case value="0.1 / (1 - 0.5 * _aux0)"/>
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
        LOCAL a
        a = 0.1
        if(fabs(x) > a){
               alpha=a*x/(1-exp(-x))
        }else{
               alpha=a/(1-0.5*x)
        }
    }
    DERIVATIVE dn {
        LOCAL a
        a = 10
        n' = alpha((v + 55)/a)}
    """)
    assert(xml_compare(mod, lems))
