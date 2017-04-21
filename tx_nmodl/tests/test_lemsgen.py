import os
from tx_nmodl.lems import mod2lems

mod = os.path.join(os.path.dirname(__file__), 'kd.mod')
with open(mod) as f:
    from xml.dom import minidom
    print()
    print(minidom.parseString(mod2lems(f.read())).toprettyxml(indent="   "))

    # http://python-xmlunittest.readthedocs.io/en/latest/xmlunittest.html#xml-documents-comparison-assertion
