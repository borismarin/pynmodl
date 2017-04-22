from textx.metamodel import metamodel_from_file


# hack to get x-refs right
class Variable(object):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name


class fakedict(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, key):
        return Variable(None, key)


def metamodel_with_any_var(path):
    return metamodel_from_file(path, classes=[Variable], builtins=fakedict())
