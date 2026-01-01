class CodeGenerator:
    def __init__(self, instructions):
        self.instructions = instructions

    def generate(self):
        # We will generate a Python script that simulates the IR using a state machine
        # to handle GOTOs.
        
        python_code = []
        python_code.append("import sys")
        python_code.append("")
        python_code.append("def main():")
        python_code.append("    # Variables")
        # We don't know all variables upfront, but Python is dynamic so it's fine.
        
        python_code.append("    label = 'start'")
        python_code.append("    while True:")
        
        # Group instructions by label
        blocks = {}
        current_label = 'start'
        blocks[current_label] = []
        
        for instr in self.instructions:
            if instr.endswith(':'):
                current_label = instr[:-1]
                blocks[current_label] = []
            else:
                blocks[current_label].append(instr)
        
        # Generate code for each block
        for label, instrs in blocks.items():
            python_code.append(f"        if label == '{label}':")
            if not instrs:
                python_code.append("            pass") # Empty block
            
            for instr in instrs:
                self.translate_instr(instr, python_code)
            
            # If block doesn't end with GOTO or RETURN, fall through to next label?
            # In IR, fallthrough is implicit. In this state machine, we need explicit transition.
            # But we don't know the "next" label easily unless we track order.
            # Let's track order of labels.
            
        # We need to handle fallthrough.
        # Let's rewrite the loop structure.
        # Instead of `if label == ...`, we can use `match` or `if/elif`.
        # And for fallthrough, we need to know the next label.
        
        return "\n".join(python_code)

    def generate_v2(self):
        # Better approach:
        # 1. Collect all labels in order.
        # 2. Generate if/elif chain.
        # 3. Handle fallthrough by setting label to next label.
        
        labels = []
        current_label = 'start'
        blocks = {current_label: []}
        labels.append(current_label)
        
        for instr in self.instructions:
            if instr.endswith(':'):
                current_label = instr[:-1]
                if current_label not in blocks:
                    blocks[current_label] = []
                    labels.append(current_label)
            else:
                blocks[current_label].append(instr)
                
        python_code = []
        python_code.append("import sys")
        python_code.append("")
        python_code.append("def run():")
        python_code.append("    label = 'start'")
        python_code.append("    while True:")
        
        for i, label in enumerate(labels):
            check = "if" if i == 0 else "elif"
            python_code.append(f"        {check} label == '{label}':")
            
            block_instrs = blocks[label]
            has_jump = False
            
            for instr in block_instrs:
                self.translate_instr(instr, python_code)
                if "GOTO" in instr or "RETURN" in instr:
                    has_jump = True
            
            if not has_jump:
                # Fallthrough to next label
                if i + 1 < len(labels):
                    next_label = labels[i+1]
                    python_code.append(f"            label = '{next_label}'")
                else:
                    python_code.append("            break") # End of program
        
        python_code.append("")
        python_code.append("if __name__ == '__main__':")
        python_code.append("    run()")
        
        return "\n".join(python_code)

    def translate_instr(self, instr, output):
        indent = "            "
        
        if instr.startswith("FUNC"):
            # Function definition in IR...
            # This approach (state machine) assumes a single function or flat code.
            # If we have multiple functions in IR, we need to handle them.
            # My IR generator produces FUNC/END_FUNC.
            # The state machine approach works for a single function body.
            # For multiple functions, we should generate Python functions?
            # But IR is flat.
            # Let's assume we generate Python functions corresponding to IR functions.
            pass
            
        # Let's handle FUNC/END_FUNC by splitting the IR into functions.
        pass

class PythonCodeGenerator:
    def __init__(self, instructions):
        self.instructions = instructions

    def generate(self):
        # Split instructions by functions
        functions = {}
        current_func = 'global' # Code outside functions? (Global vars)
        functions[current_func] = []
        
        for instr in self.instructions:
            if instr.startswith("FUNC "):
                current_func = instr.split()[1]
                functions[current_func] = []
            elif instr == "END_FUNC":
                current_func = 'global'
            else:
                functions[current_func].append(instr)
        
        output = []
        output.append("import sys")
        output.append("")
        
        # Generate global vars (if any in 'global' block)
        # My IR generator puts global var inits in 'visit_VarDecl'.
        # If they are inside Program, they are visited.
        # But IRGenerator visits Program -> declarations.
        # If declaration is VarDecl, it emits code.
        # If declaration is FuncDecl, it emits FUNC ... END_FUNC.
        # So global code is mixed or at top.
        
        # Let's process 'global' block first
        if 'global' in functions:
            # Global code usually just inits.
            # We can put them in a main function or at top level.
            # But Python executes top level.
            for instr in functions['global']:
                # These are likely global variable inits.
                # We need to handle them.
                # But wait, `t1 = 5`, `x = t1`.
                # If we put them at top level, it works.
                pass

        # We need to handle functions.
        # Each function will have its own state machine if it has labels/jumps.
        
        for func_name, instrs in functions.items():
            if func_name == 'global':
                continue
            
            output.append(f"def {func_name}(*args):")
            # Map args to params
            # IR: PARAM x
            # We need to extract params from IR or just use *args and unpack?
            # My IR has `PARAM x` instructions at the start of FUNC.
            
            params = []
            body_instrs = []
            for instr in instrs:
                if instr.startswith("PARAM "):
                    params.append(instr.split()[1])
                else:
                    body_instrs.append(instr)
            
            # Rewrite def line with params
            output[-1] = f"def {func_name}({', '.join(params)}):"
            
            # Generate body
            output.append(self.generate_body(body_instrs))
            output.append("")

        # Generate entry point
        # If there is a main function, call it.
        output.append("if __name__ == '__main__':")
        # Execute global code?
        # Global code in 'global' block might need to be executed.
        # But variables need to be accessible.
        # Let's just put global code before `if __name__`.
        
        # Actually, let's insert global code at top level.
        global_code = self.generate_body(functions.get('global', []), indent="")
        # Insert after imports
        output.insert(2, global_code)
        
        output.append("    if 'main' in globals():")
        output.append("        main()")
        
        return "\n".join(output)

    def generate_body(self, instructions, indent="    "):
        # Check if we need a state machine (labels present)
        labels = [instr[:-1] for instr in instructions if instr.endswith(':')]
        
        if not labels:
            # Straight line code
            lines = []
            lines.append(f"{indent}_args = []") # Initialize _args
            for instr in instructions:
                lines.append(indent + self.translate_simple(instr))
            return "\n".join(lines)
        
        # State machine
        lines = []
        lines.append(f"{indent}_args = []") # Initialize _args
        lines.append(f"{indent}label = 'start'")
        lines.append(f"{indent}while True:")
        
        # Split into blocks
        blocks = {}
        current_label = 'start'
        blocks[current_label] = []
        all_labels = ['start']
        
        for instr in instructions:
            if instr.endswith(':'):
                current_label = instr[:-1]
                if current_label not in blocks:
                    blocks[current_label] = []
                    all_labels.append(current_label)
            else:
                blocks[current_label].append(instr)
        
        for i, label in enumerate(all_labels):
            check = "if" if i == 0 else "elif"
            lines.append(f"{indent}    {check} label == '{label}':")
            
            block_instrs = blocks[label]
            has_jump = False
            
            if not block_instrs:
                 lines.append(f"{indent}        pass")

            for instr in block_instrs:
                trans = self.translate_simple(instr)
                if trans:
                    lines.append(f"{indent}        {trans}")
                
                if "GOTO" in instr or "RETURN" in instr:
                    has_jump = True
            
            if not has_jump:
                if i + 1 < len(all_labels):
                    next_label = all_labels[i+1]
                    lines.append(f"{indent}        label = '{next_label}'")
                else:
                    lines.append(f"{indent}        break")
                    
        return "\n".join(lines)

    def translate_simple(self, instr):
        # Handle simple instructions
        if instr.startswith("PRINT "):
            val = instr.split(" ", 1)[1]
            return f"print({val})"
        
        if instr.startswith("RETURN"):
            parts = instr.split()
            if len(parts) > 1:
                return f"return {parts[1]}"
            return "return"
        
        if instr.startswith("IF_FALSE "):
            # IF_FALSE t1 GOTO L1
            # Python: if not t1: label = 'L1'; continue
            parts = instr.split()
            cond = parts[1]
            label = parts[3]
            return f"if not {cond}: label = '{label}'; continue"
        
        if instr.startswith("GOTO "):
            label = instr.split()[1]
            return f"label = '{label}'; continue"
        
        if " = CALL " in instr:
            # t1 = CALL func
            lhs, rhs = instr.split(" = CALL ")
            # We need to handle arguments.
            # In IR: ARG x ... t1 = CALL func
            # My IR generator emits ARG instructions before CALL.
            # But in Python we need `func(arg1, arg2)`.
            # We need to collect ARGs.
            # This is tricky in a single pass line-by-line translation.
            # We need to buffer ARGs.
            pass 
            # Since we are doing line-by-line, we can't easily look back.
            # But we can use a stack for args in the generated code?
            # Or we can change IR to include args in CALL?
            # `t1 = CALL func(a, b)`
            # My IR generator:
            # visit_FunctionCall:
            #   emit ARG ...
            #   emit CALL ...
            
            # Let's modify IR generator to emit `CALL func arg1 arg2 ...`?
            # Or in `translate_simple`, we can assume `ARG` pushes to a python list `_args`.
            # `_args.append(x)`
            # `func(*_args)`
            # `_args = []`
            return f"{lhs} = {rhs}(*_args); _args = []"

        if instr.startswith("ARG "):
            val = instr.split()[1]
            # We need `_args` to be defined.
            # We can init `_args = []` at start of function.
            return f"_args.append({val})"

        if " = " in instr:
            return instr
            
        return "" # Skip unknown or empty

class AssemblyCodeGenerator:
    def __init__(self, instructions):
        self.instructions = instructions

    def generate(self):
        output = []
        output.append("; -- Mini C Assembly --")
        
        output.append("JMP __init_globals")
        
        functions = {}
        current_func = 'global'
        functions[current_func] = []
        
        for instr in self.instructions:
            if instr.startswith("FUNC "):
                current_func = instr.split()[1]
                functions[current_func] = []
            elif instr == "END_FUNC":
                current_func = 'global'
            else:
                functions[current_func].append(instr)

        # Code for functions
        for func_name, instrs in functions.items():
            if func_name == 'global': continue
            
            output.append(f"{func_name}:")
            output.append(self.generate_block(instrs))
            # Ensure RET if missing (e.g. void)
            output.append("RET")
            output.append("")

        # Code for globals and entry
        output.append("__init_globals:")
        if 'global' in functions:
            output.append(self.generate_block(functions['global']))
            
        output.append("CALL main")
        output.append("HALT")
        
        return "\n".join(output)

    def generate_block(self, instructions):
        lines = []
        args_buffer = []

        for instr in instructions:
            if not instr or instr.startswith(';'): 
                continue
                
            # Handle Labels
            if instr.endswith(':'):
                lines.append(instr)
                continue
            
            # Handle Comments
            lines.append(f"; {instr}")

            # 1. Function Call args buffering
            if instr.startswith("ARG "):
                val = instr.split()[1]
                args_buffer.append(val)
                continue
            
            if " = CALL " in instr:
                # t1 = CALL func
                lhs, rhs = instr.split(" = CALL ")
                func_name = rhs
                
                # Push args in REVERSE order
                for arg in reversed(args_buffer):
                    lines.append(f"PUSH {arg}")
                args_buffer = [] # Clear buffer
                
                lines.append(f"CALL {func_name}")
                lines.append(f"STORE {lhs}")
                continue
                
            if "CALL " in instr: # Standalone call (ignore result)
                # Should match if no assignment? My parser might not produce this for expressions.
                # But assume `CALL func` exists.
                if args_buffer: # If any args pending
                     for arg in reversed(args_buffer):
                        lines.append(f"PUSH {arg}")
                     args_buffer = []
                # Check for "CALL func"
                parts = instr.split()
                if parts[0] == "CALL":
                    lines.append(f"CALL {parts[1]}")
                    continue

            # 2. Assignment & Arithmetic
            # Format: t1 = op1 OP op2
            if " = " in instr:
                parts = instr.split(" = ")
                lhs = parts[0]
                rhs = parts[1]
                
                # Binary Ops
                ops = {
                    '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV',
                    '==': 'EQ', '!=': 'NEQ', '>': 'GT', '<': 'LT', '>=': 'GTE', '<=': 'LTE'
                }
                
                match = None
                parsed_op = False
                
                # Check for "a OP b"
                # Need careful spacing check as vars can be 'a', 'b'
                # Assumption: IR puts spaces around ops: "a + b"
                for sym, asm_op in ops.items():
                    fsym = f" {sym} "
                    if fsym in rhs:
                        op1, op2 = rhs.split(fsym, 1)
                        lines.append(f"PUSH {op1}")
                        lines.append(f"PUSH {op2}")
                        lines.append(asm_op)
                        lines.append(f"STORE {lhs}")
                        parsed_op = True
                        break
                
                if parsed_op: continue
                
                # Unary / Simple Assignment
                # "t1 = 5" or "t1 = x"
                lines.append(f"PUSH {rhs}")
                lines.append(f"STORE {lhs}")
                continue

            # 3. Control Flow
            if instr.startswith("IF_FALSE"):
                # IF_FALSE t1 GOTO L1
                _, cond, _, label = instr.split()
                lines.append(f"PUSH {cond}")
                lines.append(f"JZ {label}")
                continue
                
            if instr.startswith("GOTO"):
                label = instr.split()[1]
                lines.append(f"JMP {label}")
                continue
                
            if instr.startswith("RETURN"):
                parts = instr.split()
                if len(parts) > 1:
                    val = parts[1]
                    lines.append(f"PUSH {val}")
                else:
                    lines.append("PUSH 0") # Void return default?
                lines.append("RET")
                continue

            # 4. Other
            if instr.startswith("PRINT"):
                val = instr.split()[1]
                lines.append(f"PUSH {val}")
                lines.append("PRINT")
                continue
                
            if instr.startswith("PARAM"):
                val = instr.split()[1]
                lines.append(f"PARAM {val}")
                continue

        return "\n".join(lines)
