import sys
from mini_c_compiler.lexer import Lexer
from mini_c_compiler.parser import Parser
from mini_c_compiler.semantic import SemanticAnalyzer
from mini_c_compiler.ir import IRGenerator
from mini_c_compiler.optimizer import Optimizer
from mini_c_compiler.codegen import PythonCodeGenerator
from mini_c_compiler.core.errors import CompilerError

def compile_file(filename, output_file=None, verbose=True):
    try:
        # Read source code
        with open(filename, 'r') as f:
            source_code = f.read()
        
        if verbose:
            print("=" * 60)
            print("SOURCE CODE:")
            print("=" * 60)
            print(source_code)
            print()
        
        # Lexical Analysis
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        if verbose:
            print("=" * 60)
            print("TOKENS:")
            print("=" * 60)
            for token in tokens:
                print(token)
            print()
        
        # Syntax Analysis
        parser = Parser(tokens)
        ast = parser.parse()
        
        if verbose:
            print("=" * 60)
            print("AST:")
            print("=" * 60)
            print(ast)
            print()
        
        # Semantic Analysis
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)
        
        if verbose:
            print("=" * 60)
            print("SEMANTIC CHECK: PASSED")
            print("=" * 60)
            print()
        
        # IR Generation
        ir_generator = IRGenerator()
        ir = ir_generator.generate(ast)
        
        if verbose:
            print("=" * 60)
            print("INTERMEDIATE REPRESENTATION (IR):")
            print("=" * 60)
            for instr in ir:
                print(instr)
            print()
        
        # Optimization
        optimizer = Optimizer(ir)
        optimized_ir = optimizer.optimize()
        
        if verbose:
            print("=" * 60)
            print("OPTIMIZED IR:")
            print("=" * 60)
            for instr in optimized_ir:
                print(instr)
            print()
        
        # Code Generation
        codegen = PythonCodeGenerator(optimized_ir)
        generated_code = codegen.generate()
        
        if verbose:
            print("=" * 60)
            print("GENERATED PYTHON CODE:")
            print("=" * 60)
            print(generated_code)
            print()
        
        # Write to output file
        if output_file:
            with open(output_file, 'w') as f:
                f.write(generated_code)
            if verbose:
                print(f"Generated code written to: {output_file}")
        
        return generated_code
        
    except CompilerError as e:
        print(f"Compilation Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file.c> [output_file.py]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    compile_file(input_file, output_file)

if __name__ == '__main__':
    main()
