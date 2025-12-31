import unittest
from mini_c_compiler.codegen import PythonCodeGenerator

class TestCodegen(unittest.TestCase):
    def test_simple_program(self):
        instructions = [
            "FUNC main",
            "t1 = 5 + 10",
            "PRINT t1",
            "END_FUNC"
        ]
        codegen = PythonCodeGenerator(instructions)
        code = codegen.generate()
        
        self.assertIn("def main():", code)
        self.assertIn("t1 = 5 + 10", code)
        self.assertIn("print(t1)", code)
        self.assertIn("if __name__ == '__main__':", code)

    def test_control_flow(self):
        instructions = [
            "FUNC main",
            "t1 = 1",
            "IF_FALSE t1 GOTO L1",
            "PRINT 1",
            "GOTO L2",
            "L1:",
            "PRINT 0",
            "L2:",
            "END_FUNC"
        ]
        codegen = PythonCodeGenerator(instructions)
        code = codegen.generate()
        
        self.assertIn("while True:", code)
        self.assertIn("if label == 'start':", code)
        self.assertIn("elif label == 'L1':", code)
        self.assertIn("elif label == 'L2':", code)
        self.assertIn("if not t1: label = 'L1'; continue", code)

    def test_func_call(self):
        instructions = [
            "FUNC add",
            "PARAM a",
            "PARAM b",
            "t1 = a + b",
            "RETURN t1",
            "END_FUNC",
            "FUNC main",
            "ARG 1",
            "ARG 2",
            "t2 = CALL add",
            "PRINT t2",
            "END_FUNC"
        ]
        codegen = PythonCodeGenerator(instructions)
        code = codegen.generate()
        
        self.assertIn("def add(a, b):", code)
        self.assertIn("return t1", code)
        self.assertIn("_args.append(1)", code)
        self.assertIn("t2 = add(*_args); _args = []", code)

if __name__ == '__main__':
    unittest.main()
