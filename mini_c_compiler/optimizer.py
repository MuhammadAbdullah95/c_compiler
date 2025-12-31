import re

class Optimizer:
    def __init__(self, instructions):
        self.instructions = instructions

    def optimize(self):
        self.constant_folding()
        self.dead_code_elimination()
        return self.instructions

    def constant_folding(self):
        # Simple constant folding for binary ops: t1 = 5 + 10 -> t1 = 15
        new_instructions = []
        constants = {} # Map temp var to value

        for instr in self.instructions:
            # Check for binary op with constants
            # Format: tX = A op B
            match = re.match(r"(\w+) = (\d+) ([\+\-\*\/]) (\d+)", instr)
            if match:
                target = match.group(1)
                left = int(match.group(2))
                op = match.group(3)
                right = int(match.group(4))
                
                val = 0
                if op == '+': val = left + right
                elif op == '-': val = left - right
                elif op == '*': val = left * right
                elif op == '/': val = int(left / right) # Integer division
                
                new_instr = f"{target} = {val}"
                new_instructions.append(new_instr)
                constants[target] = val
            else:
                new_instructions.append(instr)
        
        self.instructions = new_instructions

    def dead_code_elimination(self):
        # Remove assignments to temps that are never used
        # This requires liveness analysis, but we can do a simple pass:
        # 1. Count usages of all temps.
        # 2. Remove definitions of temps with 0 usage (unless they are side-effects? No, temps are internal).
        # But wait, `x = t1` uses t1.
        
        # Iterative approach needed because removing one might make another dead.
        
        changed = True
        while changed:
            changed = False
            used_temps = set()
            
            # Scan for usages
            for instr in self.instructions:
                # Usage in RHS: = A op B, or = A, or IF_FALSE A, or RETURN A, or PRINT A, or ARG A, or CALL A (no, CALL returns to temp)
                # Regex to find words that look like temps (t\d+) on RHS
                # Split by space and check tokens?
                parts = instr.split()
                # Skip the target of assignment
                start_idx = 0
                if '=' in parts:
                    start_idx = parts.index('=') + 1
                
                for i in range(start_idx, len(parts)):
                    token = parts[i]
                    if re.match(r"^t\d+$", token):
                        used_temps.add(token)
            
            # Filter instructions
            new_instructions = []
            for instr in self.instructions:
                # Check if it defines a temp that is not used
                match = re.match(r"^(t\d+) =", instr)
                if match:
                    target = match.group(1)
                    # Special case: CALL instructions have side effects, don't remove even if result unused?
                    # Format: t1 = CALL func
                    if "CALL" in instr:
                        new_instructions.append(instr)
                    elif target in used_temps:
                        new_instructions.append(instr)
                    else:
                        changed = True # Removed dead code
                else:
                    new_instructions.append(instr)
            
            self.instructions = new_instructions
