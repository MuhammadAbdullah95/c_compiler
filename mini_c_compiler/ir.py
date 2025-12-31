from mini_c_compiler.core import ast_nodes as ast

class IRGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0

    def new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit(self, instr):
        self.instructions.append(instr)

    def generate(self, node):
        self.visit(node)
        return self.instructions

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
        if node.initializer:
            temp = self.visit(node.initializer)
            self.emit(f"{node.name} = {temp}")

    def visit_FuncDecl(self, node):
        self.emit(f"FUNC {node.name}")
        for param in node.params:
            self.emit(f"PARAM {param.name}")
        self.visit(node.body)
        self.emit("END_FUNC")

    def visit_Block(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_IfStmt(self, node):
        condition = self.visit(node.condition)
        else_label = self.new_label()
        end_label = self.new_label()
        
        self.emit(f"IF_FALSE {condition} GOTO {else_label}")
        self.visit(node.then_branch)
        self.emit(f"GOTO {end_label}")
        self.emit(f"{else_label}:")
        if node.else_branch:
            self.visit(node.else_branch)
        self.emit(f"{end_label}:")

    def visit_WhileStmt(self, node):
        start_label = self.new_label()
        end_label = self.new_label()
        
        self.emit(f"{start_label}:")
        condition = self.visit(node.condition)
        self.emit(f"IF_FALSE {condition} GOTO {end_label}")
        self.visit(node.body)
        self.emit(f"GOTO {start_label}")
        self.emit(f"{end_label}:")

    def visit_ReturnStmt(self, node):
        if node.value:
            temp = self.visit(node.value)
            self.emit(f"RETURN {temp}")
        else:
            self.emit("RETURN")

    def visit_PrintStmt(self, node):
        temp = self.visit(node.expression)
        self.emit(f"PRINT {temp}")

    def visit_ExpressionStmt(self, node):
        self.visit(node.expression)

    def visit_Assignment(self, node):
        temp = self.visit(node.value)
        self.emit(f"{node.name} = {temp}")
        return node.name # Assignments can be expressions in C, but here we treat as stmt mostly. 
                         # If used as expression, we should return the temp or variable.

    def visit_BinaryOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        temp = self.new_temp()
        self.emit(f"{temp} = {left} {node.op} {right}")
        return temp

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        temp = self.new_temp()
        self.emit(f"{temp} = {node.op} {operand}")
        return temp

    def visit_FunctionCall(self, node):
        args = []
        for arg in node.args:
            args.append(self.visit(arg))
        
        for arg in args:
            self.emit(f"ARG {arg}")
            
        temp = self.new_temp()
        self.emit(f"{temp} = CALL {node.name}")
        return temp

    def visit_Identifier(self, node):
        return node.name

    def visit_Number(self, node):
        return str(node.value)

    def visit_FloatNumber(self, node):
        return str(node.value)
