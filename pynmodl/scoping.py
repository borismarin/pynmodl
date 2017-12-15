from textx.model import parent_of_type, children_of_type


def scope_processor(model, metamodel):
    def enclosing_block(node):
        return parent_of_type('Block', node) or \
                parent_of_type('SolvableBlock', node)

    def enclosing_func(node):
        return parent_of_type('FuncDef', ref)

    for ref in children_of_type('VarRef', model):
        found = 0
        scopes = [children_of_type('Local', enclosing_block(ref)),
                  children_of_type('FuncPar', enclosing_func(ref)),
                  children_of_type('StateVariable', model),
                  children_of_type('ParDef', model),
                  children_of_type('AssignedDef', model),
                  children_of_type('ConstDef', model)]
        for scope in scopes:
            for var in scope:
                if var.name == ref.var.name:
                    ref.var = var
                    found = True
                    break
            if found:
                break
