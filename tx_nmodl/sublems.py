from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


class L(object):

    ops = {'>': '.gt.', '>=': '.geq.', '<': '.lt.', '<=': '.leq.',
           '!=': '.neq.', '==': '.eq.', '&&': '.and.', '||': '.or.'}

    def __init__(self):
        self.ct = Element('ComponentType')
        self.dynamics = SubElement(self.ct, 'Dynamics')

    def dv(self, name, val):
        SubElement(self.dynamics, 'DerivedVariable',
                   attrib={'name': name, 'value': val})

    def dxdt(self, var, val):
        SubElement(self.dynamics, 'TimeDerivative',
                   attrib={'variable': var, 'value': val})

    def cdv(self, name, cond, if_true, if_false):
        cdv = SubElement(self.dynamics, 'ConditionalDerivedVariable',
                         attrib={'name': name})
        SubElement(cdv, 'Case', attrib={'condition': cond, 'value': if_true})
        SubElement(cdv, 'Case', attrib={'value': if_false})


    def render(self):
        return minidom.parseString(tostring(self.ct)).toprettyxml(indent="   ")
