import re

class Optimizer:
    def __init__(self, instructions):
        self.instructions = instructions

    def optimize(self):
        modified = True
        pass_count = 0
        while modified and pass_count < 10: # Avoid infinite loops
            modified = False
            # Order matters: Propagation reveals Folding constants, Folding creates new Propagation opportunities
            if self.constant_propagation(): modified = True
            if self.constant_folding(): modified = True
            if self.dead_code_elimination(): modified = True
            pass_count += 1
        return self.instructions

    def constant_propagation(self):
        # Map var/temp -> constant value (int/float)
        constants = {} 
        new_instructions = []
        changed = False

        for instr in self.instructions:
            # 1. Check if instruction defines a constant: x = 5
            # We must be careful about Control Flow (Loops/Jumps).
            # A global constant map is invalid if we jump back.
            # Simple approach: Only propagate within Basic Blocks or assume single-pass validity for temps (SSA-like).
            # Our temps (t1, t2...) are SSA-like (assigned once). 
            # User vars (x, y) are NOT.
            # SAFE STRATEGY: Only propagate valid Temps (tX). Do NOT propagate user vars 'x' unless we do data-flow analysis.
            # Let's stick to 'tX' propagation for now.
            
            # Identify definitions: t1 = 5
            match_def = re.match(r"^(t\d+) = (-?\d+)$", instr)
            if match_def:
                target = match_def.group(1)
                val = match_def.group(2)
                constants[target] = val
                new_instructions.append(instr)
                continue
            
            # 2. Identify usages and replace
            # We need to replace words in the string if they match a known constant temp.
            # Avoid partial matches (t1 matches t10?). Use regex with boundary.
            
            # Construct a safe replacement function
            current_instr = instr
            for tv, val in constants.items():
                # Regex: Word boundary \b t1 \b
                # But we only replace in RHS?
                # t2 = t1 + 5.
                # If we replace LHS, `5 = ...` invalid.
                
                parts = current_instr.split(' = ', 1)
                if len(parts) == 2:
                    lhs, rhs = parts
                    # Replace in RHS
                    new_rhs = re.sub(rf"\b{tv}\b", str(val), rhs)
                    if new_rhs != rhs:
                        current_instr = f"{lhs} = {new_rhs}"
                        changed = True
                else:
                    # Statement like: PRINT t1, IF_FALSE t1 ...
                    # Replace everywhere
                    # Check if it starts with GOTO/LABEL? No, simple instr.
                    if not current_instr.endswith(':'):
                        new_instr = re.sub(rf"\b{tv}\b", str(val), current_instr)
                        if new_instr != current_instr:
                            current_instr = new_instr
                            changed = True
            
            new_instructions.append(current_instr)
            
            # If we assign to a temp, we might have just created a new constant def!
            # e.g. t2 = 5 (after replacement)
            # This will be caught in next pass or we can update `constants` now?
            # It's safer to let the next pass handle it or `constant_folding` handle it.

        if changed:
            self.instructions = new_instructions
        return changed

    def constant_folding(self):
        # Simple constant folding for binary ops: t1 = 5 + 10 -> t1 = 15
        new_instructions = []
        changed = False

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
                if new_instr != instr:
                    new_instructions.append(new_instr)
                    changed = True
                else:
                    new_instructions.append(instr)
            else:
                new_instructions.append(instr)
        
        if changed:
            self.instructions = new_instructions
        return changed

    def dead_code_elimination(self):
        # Remove assignments to temps that are never used
        changed_overall = False
        
        # Iterative inside to clean up chains: t1=5, t2=t1 -> remove t2 -> remove t1
        internal_change = True
        while internal_change:
            internal_change = False
            used_temps = set()
            
            # Scan for usages
            for instr in self.instructions:
                parts = instr.split()
                start_idx = 0
                if '=' in parts:
                    try:
                        start_idx = parts.index('=') + 1
                    except ValueError:
                        pass
                
                for i in range(start_idx, len(parts)):
                    token = parts[i]
                    # Clean punctuation
                    token = token.replace(',', '').replace(';', '') 
                    if re.match(r"^t\d+$", token):
                        used_temps.add(token)
            
            new_instructions = []
            for instr in self.instructions:
                match = re.match(r"^(t\d+) =", instr)
                if match:
                    target = match.group(1)
                    # Keep Function Calls (side effects)
                    if "CALL" in instr:
                        new_instructions.append(instr)
                    elif target in used_temps:
                        new_instructions.append(instr)
                    else:
                        internal_change = True
                        changed_overall = True
                else:
                    new_instructions.append(instr)
            
            if internal_change:
                self.instructions = new_instructions

        return changed_overall
