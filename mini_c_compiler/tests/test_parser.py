import unittest
from mini_c_compiler.lexer import Lexer
from mini_c_compiler.parser import Parser
from mini_c_compiler.core import ast_nodes as ast
from mini_c_compiler.core.errors import ParserError

class TestParser(unittest.TestCase):
    def parse(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()

    def test_var_decl(self):
        code = "int x = 5;"
        program = self.parse(code)
        self.assertIsInstance(program, ast.Program)
        self.assertEqual(len(program.declarations), 1)
        decl = program.declarations[0]
        self.assertIsInstance(decl, ast.VarDecl)
        self.assertEqual(decl.type_name, 'int')
        self.assertEqual(decl.name, 'x')
        self.assertIsInstance(decl.initializer, ast.Number)
        self.assertEqual(decl.initializer.value, 5)

    def test_func_decl(self):
        code = "int add(int a, int b) { return a + b; }"
        program = self.parse(code)
        decl = program.declarations[0]
        self.assertIsInstance(decl, ast.FuncDecl)
        self.assertEqual(decl.name, 'add')
        self.assertEqual(len(decl.params), 2)
        self.assertEqual(decl.params[0].name, 'a')
        self.assertEqual(decl.params[1].name, 'b')
        self.assertIsInstance(decl.body, ast.Block)
        self.assertIsInstance(decl.body.statements[0], ast.ReturnStmt)

    def test_if_stmt(self):
        code = "int main() { if (x > 5) { print(x); } }"
        program = self.parse(code)
        func = program.declarations[0]
        if_stmt = func.body.statements[0]
        self.assertIsInstance(if_stmt, ast.IfStmt)
        self.assertIsInstance(if_stmt.condition, ast.BinaryOp)
        self.assertIsInstance(if_stmt.then_branch, ast.Block)

    def test_while_stmt(self):
        code = "int main() { while (x < 10) { x = x + 1; } }"
        program = self.parse(code)
        func = program.declarations[0]
        while_stmt = func.body.statements[0]
        self.assertIsInstance(while_stmt, ast.WhileStmt)

    def test_expression_precedence(self):
        code = "int x = 2 + 3 * 4;"
        program = self.parse(code)
        decl = program.declarations[0]
        # 2 + (3 * 4)
        expr = decl.initializer
        self.assertIsInstance(expr, ast.BinaryOp)
        self.assertEqual(expr.op, '+')
        self.assertIsInstance(expr.right, ast.BinaryOp)
        self.assertEqual(expr.right.op, '*')

    def test_error(self):
        code = "int x ="
        with self.assertRaises(ParserError):
            self.parse(code)

if __name__ == '__main__':
    unittest.main()
