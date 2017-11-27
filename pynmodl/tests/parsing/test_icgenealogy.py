import os
import glob
import pytest
from tempfile import gettempdir
import git
from textx.metamodel import metamodel_from_file
from textx.model import children_of_type
from textx.exceptions import TextXSemanticError


@pytest.fixture
def mm():
    class Var():
        def __init__(self, parent, name, attributes):
            self.parent = parent
            self.name = name
            self.attributes = attributes
    return metamodel_from_file(
        os.path.join(os.path.dirname(__file__), '../../grammar/nmodl.tx'),
        classes=[Var],
        builtins={'t': Var(None, 't', []),
                  'usetable': Var(None, 'usetable', [])})


def get_sample(fname):
    return os.path.join(os.path.dirname(__file__),
                        '../sample_mods/icgenealogy', fname)


def test_kaxon(mm):
    blocks = mm.model_from_file(get_sample('123815_Kaxon.mod')).blocks
    (units, neuron, indep, parameter, state,
        assigned, initial, breakpoint) = blocks[:8]

    suf = children_of_type('Suffix', neuron)[0]
    assert suf.suffix == 'Kaxon'

    sol = children_of_type('Solve', breakpoint)[0]
    assert sol.solve.name == 'states'

    assert len(state.state_vars) == 1
    assert state.state_vars[0].name == 'n'


def test_nainter(mm):
    try:
        mm.model_from_file(get_sample('150288_nainter.mod'))
    except TextXSemanticError as err:
        assert 'gnaer' in str(err.args)
        # 'RANGE gnaer' should be declared as either PARAMETER or ASSIGNED
        # (even though nrnivmodl compiles it correctly)
        #  https://www.neuron.yale.edu/neuron/static/docs/help/neuron/nmodl/nmodl2.html#RANGE


def git_clone(repo_url):
    dest = os.path.join(gettempdir(), repo_url.split('/')[-1].split('.')[0])
    return git.Repo.clone_from(repo_url, dest)


def test_all_k(mm):
    def known_errors():
        errs = os.path.join(os.path.dirname(__file__), 'icg-K-semanticErrors.dat')
        with open(errs) as file:
            lines = file.read().splitlines()
        return set(lines)

    repo = git_clone('https://github.com/icgenealogy/icg-channels-K.git')
    glob_mods = os.path.join(repo.working_dir, '*/*.mod')
    # glob_mods = '/tmp/icg-channels-K/*/*.mod'
    for mod in glob.iglob(glob_mods, recursive=True):
        print('Parsing ' + mod + '...', end=':')
        if mod.split('/')[-1] in known_errors():
            print(' '.join(['Skipping', mod,
                            ', known to contain semantic errors.']))
        else:
            try:
                print(mm.model_from_file(mod))
            except UnicodeDecodeError:
                #  handle single file with non-utf8 encoding
                print(mm.model_from_file(mod, encoding='iso-8859-1'))

