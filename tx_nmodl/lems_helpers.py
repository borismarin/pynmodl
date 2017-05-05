from xml.etree.ElementTree import Element, SubElement, Comment


class ComponentTypeHelper(object):

    OPS = {'>': '.gt.', '>=': '.geq.', '<': '.lt.', '<=': '.leq.',
           '!=': '.neq.', '==': '.eq.', '&&': '.and.', '||': '.or.'}

    def __init__(self, nml_boiler=False):

        self.comp_type = Element('ComponentType')
        self.dynamics = Element('Dynamics')

        if nml_boiler:
            self.comp_type.set('extends', 'baseIonChannel')
            self.comp_type.append(
                Comment('The defs below are hardcoded for testing purposes!'))
            SubElement(self.comp_type, 'Constant', attrib={
                'dimension': 'voltage', 'name': 'MV', 'value': '1mV'})
            SubElement(self.comp_type, 'Constant', attrib={
                'dimension': 'time', 'name': 'MS', 'value': '1ms'})
            SubElement(self.comp_type, 'Requirement', attrib={
                'name': 'v', 'dimension': 'voltage'})
            self.comp_type.append(Comment('End of hardcoded defs!'))

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

    def dimensional_el(self, el_type, parent, name, dim):
        attrs = {'name': name, 'dimension': dim}
        return SubElement(parent, el_type, attrib=attrs)

    def par(self, name, dim):
        return self.dimensional_el('Parameter', self.comp_type, name, dim)

    def req(self, name, dim):
        return self.dimensional_el('Requirement', self.comp_type, name, dim)

    def exp(self, name, dim):
        return self.dimensional_el('Exposure', self.comp_type, name, dim)

    def state(self, name, dim):
        return self.dimensional_el('StateVariable', self.dynamics, name, dim)

    def render(self):
        self.comp_type.append(self.dynamics)
        return self.comp_type


class ComponentHelper(object):
    def __init__(self):
        self.par_vals = {}

    def render(self):
        self.par_vals.update({'id': self.id})
        return Element(self.id, attrib=self.par_vals)
