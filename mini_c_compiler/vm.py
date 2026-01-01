import sys
import re

class VirtualMachine:
    def __init__(self):
        self.stack = []        # Data stack
        self.call_stack = []   # Return addresses and locals
        self.memory = {}       # Global variables
        self.locals = {}       # Current local variables
        self.instructions = [] # Code memory
        self.labels = {}       # Label to IP mapping
        self.ip = 0            # Instruction Pointer
        self.func_meta = {}    # Metadata about functions (param count, etc, if needed)

    def load_program(self, program_code):
        lines = program_code.strip().split('\n')
        self.instructions = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            
            # Remove inline comments
            if ';' in line:
                line = line.split(';', 1)[0].strip()
            
            if line.endswith(':'):
                label = line[:-1]
                self.labels[label] = len(self.instructions)
            else:
                self.instructions.append(line)

    def run(self):
        self.ip = 0
        while self.ip < len(self.instructions):
            instr = self.instructions[self.ip]
            self.ip += 1
            
            try:
                self.execute(instr)
            except Exception as e:
                print(f"Runtime Error at instruction '{instr}': {e}")
                sys.exit(1)

    def execute(self, instr):
        parts = instr.split()
        op = parts[0]
        args = parts[1:]

        if op == 'PUSH':
            # Try parsing as number, else load var
            val = args[0]
            if self.is_number(val):
                self.stack.append(float(val) if '.' in val else int(val))
            else:
                # Load from locals, then globals
                if val in self.locals:
                    self.stack.append(self.locals[val])
                elif val in self.memory:
                    self.stack.append(self.memory[val])
                else:
                    raise Exception(f"Undefined variable '{val}'")

        elif op == 'POP':
            # Discard top
            self.stack.pop()

        elif op == 'STORE':
            var = args[0]
            val = self.stack.pop()
            # If variable exists in locals, update it. Else if in globals, update it.
            # If new, defaults to local (unless outside function? we don't know scope depth here easily)
            # Default: write to local if we are in a function (call_stack not empty), else global
            if self.call_stack:
                self.locals[var] = val
            else:
                self.memory[var] = val

        elif op == 'LOAD':
            # explicit load
            var = args[0]
            if var in self.locals:
                self.stack.append(self.locals[var])
            elif var in self.memory:
                self.stack.append(self.memory[var])
            else:
                raise Exception(f"Undefined variable '{var}'")

        # Arithmetic
        elif op == 'ADD':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a + b)
        elif op == 'SUB':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a - b)
        elif op == 'MUL':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a * b)
        elif op == 'DIV':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(int(a / b)) # Integer division for simplicity

        # Comparison
        elif op == 'EQ':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a == b else 0)
        elif op == 'NEQ':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a != b else 0)
        elif op == 'GT':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a > b else 0)
        elif op == 'LT':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a < b else 0)
        
        # Jumps
        elif op == 'JMP':
            label = args[0]
            self.jump_to(label)
        elif op == 'JZ': # Jump if Zero (stack top)
            label = args[0]
            val = self.stack.pop()
            if val == 0:
                self.jump_to(label)
        elif op == 'JNZ':
            label = args[0]
            val = self.stack.pop()
            if val != 0:
                self.jump_to(label)

        # IO
        elif op == 'PRINT':
            val = self.stack.pop()
            print(val)
        
        # Functions
        elif op == 'CALL':
            label = args[0]
            # Save return IP and current locals
            self.call_stack.append((self.ip, self.locals.copy()))
            # Clear locals for new scope (arguments will be popped into it)
            self.locals = {} 
            self.jump_to(label)

        elif op == 'RET':
            # Restore
            if not self.call_stack:
                # Return from main/global - End program
                self.ip = len(self.instructions)
                return
            
            return_ip, old_locals = self.call_stack.pop()
            self.ip = return_ip
            # We don't fully restore locals because we want to keep the return value?
            # Return value is on stack.
            # Local vars of the called function are gone.
            # We restore the caller's environment.
            self.locals = old_locals

        elif op == 'HALT':
            self.ip = len(self.instructions)

        else:
            # Special case for PARAM parsing (pseudo-instruction logic moved to ASM)
            # But here `PARAM x` means "pop from stack into local x"
            # Since strict stack machine:
            # Caller: PUSH b, PUSH a, CALL func
            # Func: PARAM a (pop), PARAM b (pop)
            # This means Func gets 'a' from top (which was pushed last).
            # So Caller must push args in REVERSE order if we want standard A, B mapping?
            # OR we match:
            # Function `add(a, b)` -> IR `PARAM a`, `PARAM b`.
            # If we EXECUTE `PARAM a`: a = pop().
            # If Stack is `[..., arg1, arg2]`. Top is arg2.
            # `PARAM a` gets arg2. `PARAM b` gets arg1.
            # So `a` gets `b`'s value. 
            # To fix: Caller must PUSH args in REVERSE order (Last arg first).
            if op == 'PARAM':
                var = args[0]
                val = self.stack.pop()
                self.locals[var] = val
            
            else:
                pass # Ignore unknown

    def jump_to(self, label):
        if label not in self.labels:
            raise Exception(f"Unknown label '{label}'")
        self.ip = self.labels[label]

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python vm.py <file.asm>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        code = f.read()
    
    vm = VirtualMachine()
    vm.load_program(code)
    vm.run()
