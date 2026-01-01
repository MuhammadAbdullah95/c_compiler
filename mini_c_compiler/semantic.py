from mini_c_compiler.core import ast_nodes as ast
from mini_c_compiler.core.symbol_table import SymbolTable, Symbol
from mini_c_compiler.core.errors import SemanticError

class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope
        self.current_function_return_type = None

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
            raise SemanticError(f"[{node.name}] Variable already declared in this scope", 0)
        
        # Check initializer
        if node.initializer:
            init_type = self.visit(node.initializer)
            if init_type != node.type_name:
                # Allow implicit int -> float? Only if strictly required. 
                # Let's be strict: Error if mismatch.
                # Actually, int -> float is usually okay. float -> int is lossy.
                if node.type_name == 'float' and init_type == 'int':
                    pass # Implicit promotion
                else:
                    raise SemanticError(f"[{node.name}] Type mismatch in declaration. Expected {node.type_name}, got {init_type}", 0)
        
        symbol = Symbol(node.name, node.type_name, 'var')
        self.current_scope.define(symbol)
        
        return node.type_name

    def visit_FuncDecl(self, node):
        if self.current_scope.lookup(node.name, current_scope_only=True):
            raise SemanticError(f"[{node.name}] Function already declared", 0)
        
        param_types = [p.type_name for p in node.params]
        symbol = Symbol(node.name, node.return_type, 'func', param_types)
        self.current_scope.define(symbol)
        
        # Function scope
        previous_scope = self.current_scope
        self.current_scope = SymbolTable(parent=previous_scope)
        
        previous_return_type = self.current_function_return_type
        self.current_function_return_type = node.return_type
        
        for param in node.params:
            if self.current_scope.lookup(param.name, current_scope_only=True):
                raise SemanticError(f"[{node.name}] Duplicate parameter '{param.name}'", 0)
            param_symbol = Symbol(param.name, param.type_name, 'var')
            self.current_scope.define(param_symbol)
            
        self.visit(node.body)
        
        self.current_scope = previous_scope
        self.current_function_return_type = previous_return_type

    def visit_Block(self, node):
        previous_scope = self.current_scope
        self.current_scope = SymbolTable(parent=previous_scope)
        
        for stmt in node.statements:
            self.visit(stmt)
            
        self.current_scope = previous_scope

    def visit_IfStmt(self, node):
        self.visit(node.condition) # Should check if boolean/int?
        self.visit(node.then_branch)
        if node.else_branch:
            self.visit(node.else_branch)

    def visit_WhileStmt(self, node):
        self.visit(node.condition)
        self.visit(node.body)

    def visit_ReturnStmt(self, node):
        if node.value:
            val_type = self.visit(node.value)
            expected = self.current_function_return_type
            if val_type != expected and expected != 'void':
                 if expected == 'float' and val_type == 'int':
                     pass
                 else:
                     raise SemanticError(f"Return type mismatch. Expected {expected}, got {val_type}", 0)
        else:
            if self.current_function_return_type != 'void' and self.current_function_return_type is not None:
                raise SemanticError(f"Return value expected for function returning {self.current_function_return_type}", 0)

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
        
        val_type = self.visit(node.value)
        var_type = symbol.type_name

        if var_type != val_type:
            if var_type == 'float' and val_type == 'int':
                pass
            else:
                raise SemanticError(f"Type mismatch in assignment to '{node.name}'. Expected {var_type}, got {val_type}", 0)
        
        return var_type

    def visit_BinaryOp(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        
        # Arithmetic Ops
        if node.op in ['+', '-', '*', '/']:
            if left_type == 'float' or right_type == 'float':
                return 'float'
            return 'int'
        
        # Relational Ops
        if node.op in ['==', '!=', '>', '<', '>=', '<=']:
            return 'int' # C uses int for boolean

        return 'int'

    def visit_UnaryOp(self, node):
        return self.visit(node.operand)

    def visit_FunctionCall(self, node):
        symbol = self.current_scope.lookup(node.name)
        if not symbol:
            raise SemanticError(f"Function '{node.name}' not declared", 0)
        if symbol.category != 'func':
            raise SemanticError(f"'{node.name}' is not a function", 0)
        
        # Check argument count
        if len(node.args) != len(symbol.params):
            raise SemanticError(f"Function '{node.name}' expects {len(symbol.params)} arguments, got {len(node.args)}", 0)
            
        # Check argument types
        for i, arg in enumerate(node.args):
            arg_type = self.visit(arg)
            expected_type = symbol.params[i]
            if arg_type != expected_type:
                if expected_type == 'float' and arg_type == 'int':
                    pass
                else:
                    raise SemanticError(f"Argument {i+1} of '{node.name}' type mismatch. Expected {expected_type}, got {arg_type}", 0)
        
        return symbol.type_name # Return type of function

    def visit_Identifier(self, node):
        symbol = self.current_scope.lookup(node.name)
        if not symbol:
            raise SemanticError(f"Variable '{node.name}' not declared", 0)
        return symbol.type_name

    def visit_Number(self, node):
        return 'int'

    def visit_FloatNumber(self, node):
        return 'float'
