import os
from hack import metamodel_with_any_var
from textx.model import children_of_type


mm = metamodel_with_any_var(
    os.path.join(os.path.dirname(__file__), '../../grammar/table.tx'))


def test_full():
    s = """
    TABLE minf, mexp, hinf, hexp, ninf, nexp 
            DEPEND dt, celsius FROM -100 TO 100 WITH 200
    """
    table = mm.model_from_str(s)
    assert len(table.tabbed) == 6
    assert table.tabbed[1].var.name == 'mexp'
    assert table.depend.deps[0].var.name == 'dt'
    assert table.f.val == -100
    assert table.t.val == 100
    assert table.w.val == 200


def test_depend_safevar():
    s = "TABLE DEPEND shiftm FROM -150 TO 150 WITH 200"
    table = mm.model_from_str(s)
    assert table.depend.deps[0].var.name == 'shiftm'
    assert table.f.val == -150
    assert table.t.val == 150
    assert table.w.val == 200
