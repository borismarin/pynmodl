import os
from pynmodl.lems import mod2lems

def get_sample(fname):
    return os.path.join(os.path.dirname(__file__), '../../sample_mods', fname)

with open(get_sample('kd.mod')) as f:
    from xml.dom import minidom
    print(minidom.parseString(mod2lems(f.read())).toprettyxml(indent="   "))

with open(get_sample('na.mod')) as f:
    from xml.dom import minidom
    print(minidom.parseString(mod2lems(f.read())).toprettyxml(indent="   "))
