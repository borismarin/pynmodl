import os
from textx.metamodel import metamodel_from_file


class ExprCompiler(object):
    def __init__(self):
        self.mm = metamodel_from_file(
            os.path.join(os.path.dirname(__file__), 'expressions.tx'))
        self.mm.register_obj_processors({
            'Addition': self.addition,
            'Multiplication': self.multiplication,
            'Exponentiation': self.exponentiation,
            'Negation': self.negation,
            'Paren': self.paren,
            'FuncCall': self.funccall,
            'Num': self.num,
            'VarRef': self.varref,
            'PlusOrMinus': self.pm,
            'MulOrDiv': self.md,
            'Exp': self.exp,
            'Assignment': self.assign,
            'IfStatement': self.ifstmt,
            'Relational': self.relational,
            'LogicalCon': self.logicalcon,
            'Block': self.block,
            'RelOp': self.relop,
            'LogCon': self.logcon,
            'FuncDef': self.funcdef,
            'Locals': self.locals,
            'FuncPar': self.funcpar,
            'Primed': self.primed,
            'Local': self.local,
        })

    def t(self, type_str):
        return self.mm.namespaces[None][type_str]

    def is_txtype(self, obj, type_str):
        return isinstance(obj, self.t(type_str))
