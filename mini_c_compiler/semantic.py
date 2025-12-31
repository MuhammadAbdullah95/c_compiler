from mini_c_compiler.core import ast_nodes as ast
from mini_c_compiler.core.symbol_table import SymbolTable, Symbol
from mini_c_compiler.core.errors import SemanticError

class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope

    def analyze(self, node):
        self.visit(node)

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')

    def visit_Program(self, node):
        for decl in node.declarations:
            self.visit(decl)

    def visit_VarDecl(self, node):
        if self.current_scope.lookup(node.name, current_scope_only=True):
            raise SemanticError(f"Variable '{node.name}' already declared in this scope", 0) # Line number not passed in AST yet, need to improve AST
        
        # Visit initializer to check for usage of undeclared vars
        if node.initializer:
            self.visit(node.initializer)
        
        symbol = Symbol(node.name, node.type_name, 'var')
        self.current_scope.define(symbol)

    def visit_FuncDecl(self, node):
        if self.current_scope.lookup(node.name, current_scope_only=True):
            raise SemanticError(f"Function '{node.name}' already declared", 0)
        
        param_types = [p.type_name for p in node.params]
        symbol = Symbol(node.name, node.return_type, 'func', param_types)
        self.current_scope.define(symbol)
        
        # Function scope
        previous_scope = self.current_scope
        self.current_scope = SymbolTable(parent=previous_scope)
        
        for param in node.params:
            if self.current_scope.lookup(param.name, current_scope_only=True):
                raise SemanticError(f"Duplicate parameter '{param.name}'", 0)
            param_symbol = Symbol(param.name, param.type_name, 'var')
            self.current_scope.define(param_symbol)
            
        self.visit(node.body)
        
        self.current_scope = previous_scope

    def visit_Block(self, node):
        # Blocks usually create a new scope, but for function body we might want to reuse the scope created in FuncDecl?
        # In this implementation, FuncDecl creates a scope for params.
        # If we create another scope here, params are in parent scope. That works.
        # But standard C: params are in the function's block scope.
        # Let's just create a new scope for every block.
        
        previous_scope = self.current_scope
        self.current_scope = SymbolTable(parent=previous_scope)
        
        for stmt in node.statements:
            self.visit(stmt)
            
        self.current_scope = previous_scope

    def visit_IfStmt(self, node):
        self.visit(node.condition)
        self.visit(node.then_branch)
        if node.else_branch:
            self.visit(node.else_branch)

    def visit_WhileStmt(self, node):
        self.visit(node.condition)
        self.visit(node.body)

    def visit_ReturnStmt(self, node):
        if node.value:
            self.visit(node.value)

    def visit_PrintStmt(self, node):
        self.visit(node.expression)

    def visit_ExpressionStmt(self, node):
        self.visit(node.expression)

    def visit_Assignment(self, node):
        symbol = self.current_scope.lookup(node.name)
        if not symbol:
            raise SemanticError(f"Variable '{node.name}' not declared", 0)
        if symbol.category != 'var':
            raise SemanticError(f"Cannot assign to '{node.name}' which is a {symbol.category}", 0)
        
        self.visit(node.value)

    def visit_BinaryOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOp(self, node):
        self.visit(node.operand)

    def visit_FunctionCall(self, node):
        symbol = self.current_scope.lookup(node.name)
        if not symbol:
            raise SemanticError(f"Function '{node.name}' not declared", 0)
        if symbol.category != 'func':
            raise SemanticError(f"'{node.name}' is not a function", 0)
        
        if len(node.args) != len(symbol.params):
            raise SemanticError(f"Function '{node.name}' expects {len(symbol.params)} arguments, got {len(node.args)}", 0)
            
        for arg in node.args:
            self.visit(arg)

    def visit_Identifier(self, node):
        symbol = self.current_scope.lookup(node.name)
        if not symbol:
            raise SemanticError(f"Variable '{node.name}' not declared", 0)

    def visit_Number(self, node):
        pass

    def visit_FloatNumber(self, node):
        pass
