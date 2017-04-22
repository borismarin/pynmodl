from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from tx_nmodl.nmodl import NModl


class LemsCompTypeGenerator(NModl):
    def __init__(self):
        super().__init__()
        self.mm.register_obj_processors({
            'Suffix': self.handle_suffix,
            'Read': self.handle_read,    # from USEION
            'Write': self.handle_write,  # from USEION
        })
        self.xml_skeleton()

    def handle_suffix(self, suf):
        self.comp_type.attrib['id'] = suf.suffix

    def handle_read(self, read):
        for r in read.reads:
            self.subel('Requirement', {'name': r.name, 'dimension': 'none'})

    def handle_write(self, write):
        for w in write.writes:
            self.subel('Exposure', {'name': w.name, 'dimension': 'none'})

    def subel(self, type, attrs):
        return SubElement(self.where[type], type, attrib=attrs)

    def compile(self, string):
        self.mm.model_from_str(string)
        return self.comp_type

    def xml_skeleton(self):
        self.comp_type = Element('ComponentType', attrib={
            'extends': 'baseIonChannel'})
        self.comp_type.append(
            Comment('The defs below are hardcoded for testing purposes!'))
        SubElement(self.comp_type, 'Constant', attrib={
            'dimension': 'voltage', 'name': 'MV', 'value': '1mV'})
        SubElement(self.comp_type, 'Constant', attrib={
            'dimension': 'time', 'name': 'MS', 'value': '1ms'})
        SubElement(self.comp_type, 'Requirement', attrib={
            'name': 'v', 'dimension': 'voltage'})
        self.comp_type.append(Comment('End of hardcoded defs!'))
        self.dynamics = Element('Dynamics')
        self.where = {'Parameter': self.comp_type, 'Requirement':
                      self.comp_type, 'Exposure': self.comp_type,
                      'DerivedVariable': self.dynamics, 'StateVariable':
                      self.dynamics}


def mod2lems(mod_string):

    root = Element('neuroml')
    root.append(LemsCompTypeGenerator().compile(mod_string))

    return tostring(root)
