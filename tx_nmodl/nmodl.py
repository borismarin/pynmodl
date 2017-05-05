import os
from textx.metamodel import metamodel_from_file

class NModl(object):
    def __init__(self):
        curr_dir = os.path.dirname(__file__)
        self.mm = metamodel_from_file(
            os.path.join(curr_dir, 'grammar', 'nmodl.tx'))
