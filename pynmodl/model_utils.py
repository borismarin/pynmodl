from textx.model import children_of_type, metamodel


# should probably go into handcoded 'FuncDef' class
def side_effects(funcdef):
    if funcdef.is_procedure:
        side_effs = [asgn.variable.name
                     for asgn in children_of_type('Assignment', funcdef)
                     if is_assignment(asgn)
                     and not isinstance(asgn.variable, 'Local')]
    else:
        side_effs = []
    return side_effs


# should probably go into handcoded 'Expression' class
def expr_t(node, type_name):
    return metamodel(node).namespaces['expressions'][type_name]


def is_assignment(node):
    return all((getattr(node, 'variable', False),
               isinstance(node, expr_t(node, 'Assignment'))))


def is_composite(node):
    return len(children_of_type('Negation', node)) > 1


def has_func_calls(node):
    return len(children_of_type('FuncCall', node)) > 0
