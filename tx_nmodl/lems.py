from tx_nmodl.nmodl import NModl


class NModlLems(NModl):
    def __init__(self):
        super().__init__()
        self.mm.register_obj_processors({
            'Title': self.handle_title
        })

    def handle_title(self, title):
        print(title.title)

    def compile(self, string):
        return self.mm.model_from_str(string)

