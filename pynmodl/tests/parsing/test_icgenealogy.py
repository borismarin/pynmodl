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


#@pytest.mark.xfail
def test_all_k(mm):
    repo = git_clone('https://github.com/icgenealogy/icg-channels-K.git')
    glob_mods = os.path.join(repo.working_dir, '*/*.mod')
    # glob_mods = '/tmp/icg-channels-K/*/*.mod'
    for mod in glob.iglob(glob_mods, recursive=True):
        print('Parsing ' + mod + '...', end=':')
        if mod.split('/')[-1] in ['105385_kleak_gp.mod', '150288_nainter.mod',
                                  '113446_kir.mod', '114685_AXNODE75.mod',
                                  '119266_hha2.mod', '119266_hha_old.mod',
                                  '123815_hha2.mod', '123815_hha_old.mod',
                                  '123815_ichan2.mod', '123815_ichan2_icgK2.mod',
                                  '124291_ichan2.mod', '124291_ichan2_icgK2.mod',
                                  '124513_ichan2.mod', '124513_ichan2_icgK2.mod',
                                  '125385_skaprox.mod', '125385_skm.mod',
                                  '125385_skv.mod', '127507_newhh3.mod',
                                  '127507_newhh3_icgK2.mod', '127992_HHmicro.mod',
                                  '135902_CA1ika.mod', '135902_CA1ika_icgK2.mod',
                                  '135902_CA1ikdr.mod', '135902_kapyrkop.mod',
                                  '135902_kdrpyrkop.mod', '135903_CA1ika.mod',
                                  '135903_CA1ika_icgK2.mod', '135903_kapyrkop.mod',
                                  '135903_kdrpyrkop.mod', '136309_kdr_Yu.mod',
                                  '139421_CA1ika.mod', '139421_CA1ika_icgK2.mod',
                                  '139421_kapyrkop.mod', '139421_kdrpyrkop.mod',
                                  '141063_dr.mod', '144450_hha2.mod', 
                                  '144450_hha_old.mod', '144490_hha2.mod',
                                  '144490_hha2_v2.mod', '144490_hha_old.mod',
                                  '144490_hha_old_v2.mod', '144520_ik1.mod',
                                  '144520_ikd.mod', '144520_ito.mod',
                                  '147460_AXNODE.mod', '147460_AXNODE_icgK2.mod',
                                  '151282_CA3ika.mo', '151282_CA3ika.mod',
                                  '151282_CA3ika_icgK2.mod', '155157_AType_potassium.mod',
                                  '155568_ichan2.mod' '155568_ichan2_icgK2.mod',
                                  '155568_ichan2.mod', '155568_ichan2_icgK2.mod',
                                  '155601_ichan2.mod','155601_ichan2_icgK2.mod',
                                  '155602_ichan2.mod', '155602_ichan2_icgK2.mod', 
                                  '155735_Kh1.mod', '181967_hha2_icgK.mod',
                                  '181967_hha_old_icgK.mod', '181967_ichan2_icgK.mod',
                                  '181967_ichan2_icgK2.mod', '182134_kaolmkop.mod',
                                  '182134_kapyrkop.mod', '182134_kdrbwb.mod', 
                                  '182134_kdrolmkop.mod', '182134_kdrpr.mod',
                                  '182134_kdrpyrkop.mod', '182988_dr_icgK.mod',
                                  '185858_kdrbwb.mod', '19696_kadist.mod',
                                  '19746_M99Ka.mod', '20212_hha.mod', '20212_hha2.mod',
                                  '20212_hha_old.mod','21329_nethhwbm.mod', 
                                  '26997_kdr.mod', '33975_kdr.mod', '3454_ht.mod',
                                  '3454_lt.mod', '35358_kdr.mod', '37819_kdr.mod',
                                  '37819_kmbg.mod', '3800_ikur.mod', '51022_fh.mod',
                                  '51781_ichan2.mod', '51781_ichan2_icgK2.mod',
                                  '64229_ichan2.mod', '64229_ichan2_icgK2.mod',
                                  '64229_k2RT03.mod', '64229_k2RT03_v2.mod',
                                  '64229_kaRT03.mod', '64229_kaRT03_v2.mod', 
                                  '64229_kdr.mod', '64229_kdr_v2.mod',
                                  '64229_kdrp.mod', '64229_kdrp_v2.mod',
                                  '64229_kdrRT03.mod', '64229_kdrRT03_v2.mod',
                                  '64229_kmRT03.mod', '64229_kmRT03_v2.mod',
                                  '7399_kdr.mod', '7400_kdr.mod', '84589_kadist.mod',
                                  '84589_kaprox.mod', '84589_kd.mod', '84589_kk.mod',
                                  '84589_km.mod', '87473_fn.mod', '87585_ichanR859C1.mod',
                                  '87585_ichanWT2005.mod','97917_ichan2.mod',
                                  '97917_ichan2_icgK2.mod']:
            # Reasons for skipping
            # 105385_kleak_gp.mod, 150288_nainter.mod, 114685_AXNODE75.mod,
            # 119266_hha2.mod, 119266_hha_old.mod, 123815_hha2.mod, 
            # 123815_ichan2.mod, 123815_ichan2_icgK2.mod
            # 124291_ichan2.mod, 124291_ichan2_icgK2.mod 123815_hha_old.mod,
            # 124513_ichan2.mod, 124513_ichan2_icgK2.mod, 127507_newhh3.mod,
            # 127507_newhh3_icgK2.mod, 127992_HHmicro.mod, 135902_CA1ika.mod,
            # 135902_CA1ika_icgK2.mod, 135902_CA1ikdr.mod, 135903_CA1ika.mod,
            # 135903_CA1ika_icgK2.mod, 135903_kapyrkop.mod, 135903_kdrpyrkop.mod,
            # 136309_kdr_Yu.mod, 139421_CA1ika.mod, 139421_CA1ika.mod, 
            # 139421_CA1ika.mod, 139421_CA1ika_icgK2.mod, 141063_dr.mod, 
            # 144450_hha2.mod, 144450_hha_old.mod, 144490_hha2.mod, 
            # 144490_hha2_v2.mod, 144490_hha_old.mod, 144490_hha_old_v2.mod: 
            # 147460_AXNODE.mod, 147460_AXNODE_icgK2.mod, 151282_CA3ika.mod,
            # 151282_CA3ika.mod, 151282_CA3ika_icgK2.mod, 155157_AType_potassium.mod,
            # 155568_ichan2.mod 155568_ichan2_icgK2.mod, 155568_ichan2.mod,
            # 155568_ichan2_icgK2.mod, 155601_ichan2.mod, 155601_ichan2_icgK2.mod,
            # 155602_ichan2.mod, 155602_ichan2_icgK2.mod, 155735_Kh1.mod,
            # 181967_hha2_icgK.mod, 181967_hha_old_icgK.mod, 181967_ichan2_icgK.mod
            # 181967_ichan2_icgK2.mod, 182988_dr_icgK.mod, 19746_M99Ka.mod,
            # 20212_hha.mod, 20212_hha2.mod, 20212_hha_old.mod, 21329_nethhwbm.mod,
            # 3454_ht.mod, 3454_lt.mod, 35358_kdr.mod, 37819_kdr.mod, 37819_kmbg.mod,
            # 3800_ikur.mod, 51781_ichan2.mod, 51781_ichan2_icgK2.mod, 64229_ichan2.mod,
            # 64229_ichan2_icgK2.mod, 87473_fn.mod, 87585_ichanR859C1.mod,
            # 87585_ichanWT2005.mod, 97917_ichan2.mod, 97917_ichan2_icgK2.mod
            #   these modfiles declare RANGE variables without corresponding
            #   PARAMETER or ASSIGNED (or READ) declarations
            # 113446_kir.mod: qna in COMPARTMENT statement is not a state var
            # 125385_skaprox.mod, 125385_skm.mod, 125385_skv.mod: 
            #   function imported via VERBATIM extern
            # 135902_kapyrkop.mod, 135902_kdrpyrkop.mod, 139421_kapyrkop.mod,
            # 139421_kdrpyrkop.mod, 147460_AXNODE.mod, 182134_kdrpyrkop.mod: 
            #   function 'max' (probably) defined at external .inc file
            # 144520_ik1.mod, 144520_ikd.mod, 144520_ito.mod:
            #    Constant S (probably) defined at external .inc file
            # 182134_kaolmkop.mod, 182134_kapyrkop.mod, 182134_kdrbwb.mod,
            # 182134_kdrolmkop.mod, 182134_kdrpr.mod, 185858_kdrbwb.mod:
            #    function 'fun2/3' (probably) defined at external .inc file
            # 19696_kadist.mod: celsius should be a param
            # 26997_kdr.mod, 33975_kdr.mod, 64229_k2RT03.mod, 64229_k2RT03_v2.mod,
            # 64229_kaRT03.mod, 64229_kaRT03_v2.mod, 64229_kdr.mod, 64229_kdr_v2.mod,
            # 64229_kdrp.mod, 64229_kdrp_v2.mod, 64229_kdrRT03.mod, 64229_kdrRT03_v2.mod,
            # 64229_kmRT03.mod, 64229_kmRT03_v2.mod, 7399_kdr.mod, 7400_kdr.mod
            #    use of undeclared variable in procedure
            # 51022_fh.mod: 
            #    constant FARADAY (probably) defined at external .inc file
            # 84589_kadist.mod, 84589_kaprox.mod, 84589_kd.mod, 84589_kk.mod,
            # 84589_km.mod
            #    most of the model (probably) defined at external .inc file
            print(' '.join(['Skipping', mod,
                            ', known to contain semantic errors.']))
        else:
            try:
                print(mm.model_from_file(mod))
            except UnicodeDecodeError:
                #  handle single file with non-utf8 encoding
                print(mm.model_from_file(mod, encoding='iso-8859-1'))

