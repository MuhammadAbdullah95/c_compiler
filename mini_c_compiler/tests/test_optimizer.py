import unittest
from mini_c_compiler.optimizer import Optimizer

class TestOptimizer(unittest.TestCase):
    def test_constant_folding(self):
        instructions = [
            "t1 = 5 + 10",
            "x = t1"
        ]
        optimizer = Optimizer(instructions)
        optimized = optimizer.optimize()
        
        self.assertIn("t1 = 15", optimized)
        self.assertIn("x = t1", optimized)

    def test_dead_code_elimination(self):
        instructions = [
            "t1 = 5 + 10", # t1 used in t2
            "t2 = t1 + 5", # t2 unused
            "x = 10"
        ]
        optimizer = Optimizer(instructions)
        optimized = optimizer.optimize()
        
        # t2 should be removed
        self.assertFalse(any("t2 =" in instr for instr in optimized))
        # t1 should be removed because t2 was removed?
        # My implementation is iterative.
        # Pass 1: t2 unused -> remove t2.
        # Pass 2: t1 unused -> remove t1.
        self.assertFalse(any("t1 =" in instr for instr in optimized))
        self.assertIn("x = 10", optimized)

    def test_preserve_side_effects(self):
        instructions = [
            "t1 = CALL func", # t1 unused but CALL has side effects
            "x = 10"
        ]
        optimizer = Optimizer(instructions)
        optimized = optimizer.optimize()
        
        self.assertTrue(any("CALL func" in instr for instr in optimized))
        self.assertIn("x = 10", optimized)

if __name__ == '__main__':
    unittest.main()
