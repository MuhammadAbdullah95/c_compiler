from dataclasses import dataclass
from typing import List, Optional, Union

@dataclass
class ASTNode:
    pass

# Expressions
@dataclass
class Expression(ASTNode):
    pass

@dataclass
class Number(Expression):
    value: int

@dataclass
class FloatNumber(Expression):
    value: float

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression

@dataclass
class UnaryOp(Expression):
    op: str
    operand: Expression

@dataclass
class FunctionCall(Expression):
    name: str
    args: List[Expression]

# Statements
@dataclass
class Statement(ASTNode):
    pass

@dataclass
class Assignment(Statement):
    name: str
    value: Expression

@dataclass
class ReturnStmt(Statement):
    value: Optional[Expression]

@dataclass
class PrintStmt(Statement):
    expression: Expression

@dataclass
class ExpressionStmt(Statement):
    expression: Expression

@dataclass
class Block(Statement):
    statements: List[Statement]

@dataclass
class IfStmt(Statement):
    condition: Expression
    then_branch: Block
    else_branch: Optional[Block]

@dataclass
class WhileStmt(Statement):
    condition: Expression
    body: Block

@dataclass
class VarDecl(Statement):
    type_name: str
    name: str
    initializer: Optional[Expression]

# Declarations
@dataclass
class Param(ASTNode):
    type_name: str
    name: str

@dataclass
class FuncDecl(ASTNode):
    return_type: str
    name: str
    params: List[Param]
    body: Block

@dataclass
class Program(ASTNode):
    declarations: List[Union[VarDecl, FuncDecl]]
