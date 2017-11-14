import os
from textx.metamodel import metamodel_from_file
from textx.model import children_of_type


mm = metamodel_from_file(
    os.path.join(os.path.dirname(__file__), '../../grammar/nmodl.tx'))


def get_sample(fname):
    return os.path.join(os.path.dirname(__file__),
                        '../sample_mods/icgenealogy', fname)


def test_kaxon():
    blocks = mm.model_from_file(get_sample('123815_Kaxon.mod')).blocks
    (units, neuron, indep, parameter, state,
        assigned, initial, breakpoint) = blocks[:8]

    suf = children_of_type('Suffix', neuron)[0]
    assert suf.suffix == 'Kaxon'

    sol = children_of_type('Solve', breakpoint)[0]
    assert sol.solve.name == 'states'

    assert len(state.state_vars) == 1
    assert state.state_vars[0].name == 'n'
