import unittest
from mini_c_compiler.lexer import Lexer
from mini_c_compiler.parser import Parser
from mini_c_compiler.semantic import SemanticAnalyzer
from mini_c_compiler.core.errors import SemanticError

class TestSemantic(unittest.TestCase):
    def analyze(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)

    def test_valid_program(self):
        code = """
        int x = 5;
        int add(int a, int b) {
            return a + b;
        }
        int main() {
            int y = add(x, 10);
            if (y > 10) {
                print(y);
            }
        }
        """
        self.analyze(code)

    def test_redeclaration_var(self):
        code = """
        int x = 5;
        int x = 10;
        """
        with self.assertRaises(SemanticError) as cm:
            self.analyze(code)
        self.assertIn("already declared", str(cm.exception))

    def test_undeclared_var(self):
        code = """
        int main() {
            x = 5;
        }
        """
        with self.assertRaises(SemanticError) as cm:
            self.analyze(code)
        self.assertIn("not declared", str(cm.exception))

    def test_func_arg_mismatch(self):
        code = """
        int add(int a, int b) { return a + b; }
        int main() {
            add(1);
        }
        """
        with self.assertRaises(SemanticError) as cm:
            self.analyze(code)
        self.assertIn("expects 2 arguments", str(cm.exception))

    def test_scope_shadowing(self):
        # Shadowing is usually allowed in C, but my implementation might flag it if I check parent scopes?
        # My implementation: `lookup(name, current_scope_only=True)` for declaration check.
        # So shadowing should be allowed.
        code = """
        int x = 5;
        int main() {
            int x = 10;
            print(x);
        }
        """
        self.analyze(code)

    def test_use_before_decl(self):
        code = """
        int main() {
            x = 5;
            int x = 10;
        }
        """
        with self.assertRaises(SemanticError):
            self.analyze(code)

if __name__ == '__main__':
    unittest.main()
