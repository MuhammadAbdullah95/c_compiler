import unittest
from mini_c_compiler.lexer import Lexer
from mini_c_compiler.parser import Parser
from mini_c_compiler.ir import IRGenerator

class TestIR(unittest.TestCase):
    def generate_ir(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        ir_gen = IRGenerator()
        return ir_gen.generate(ast)

    def test_arithmetic(self):
        code = "int x = 5 + 3 * 2;"
        ir = self.generate_ir(code)
        # Expected:
        # t1 = 3 * 2
        # t2 = 5 + t1
        # x = t2
        
        self.assertTrue(any("= 3 * 2" in instr for instr in ir))
        self.assertTrue(any("= 5 +" in instr for instr in ir))
        self.assertTrue(any("x =" in instr for instr in ir))

    def test_if_stmt(self):
        code = "int main() { if (x > 5) { print(x); } }"
        ir = self.generate_ir(code)
        # Expected:
        # FUNC main
        # t1 = x > 5
        # IF_FALSE t1 GOTO L1
        # PRINT x
        # GOTO L2
        # L1:
        # L2:
        # END_FUNC
        
        self.assertTrue(any("IF_FALSE" in instr for instr in ir))
        self.assertTrue(any("GOTO" in instr for instr in ir))
        self.assertTrue(any(":" in instr for instr in ir))

    def test_while_stmt(self):
        code = "int main() { while (x < 10) { x = x + 1; } }"
        ir = self.generate_ir(code)
        
        self.assertTrue(any("IF_FALSE" in instr for instr in ir))
        self.assertTrue(any("GOTO" in instr for instr in ir))

    def test_func_call(self):
        code = "int main() { add(1, 2); }"
        ir = self.generate_ir(code)
        
        self.assertTrue(any("ARG 1" in instr for instr in ir))
        self.assertTrue(any("ARG 2" in instr for instr in ir))
        self.assertTrue(any("CALL add" in instr for instr in ir))

if __name__ == '__main__':
    unittest.main()
