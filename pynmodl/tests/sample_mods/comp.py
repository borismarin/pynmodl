from xml.dom.minidom import parseString
from pynmodl.lems import mod2lems
from pynmodl.unparser import Unparser

with open('na.mod') as f:
    na = f.read()
    print(parseString(mod2lems(na)).toprettyxml())
    print(Unparser().compile(na))