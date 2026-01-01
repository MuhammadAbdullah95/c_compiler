import sys
import os
from mini_c_compiler.lexer import Lexer
from mini_c_compiler.parser import Parser
from mini_c_compiler.semantic import SemanticAnalyzer
from mini_c_compiler.ir import IRGenerator
from mini_c_compiler.optimizer import Optimizer
from mini_c_compiler.codegen import PythonCodeGenerator, AssemblyCodeGenerator
from mini_c_compiler.visualizer import ASTVisualizer
from mini_c_compiler.core.errors import CompilerError

def compile_file(filename, output_file=None, verbose=True, target='python', visualize=False):
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
            
        if visualize:
            viz = ASTVisualizer()
            dot_content = viz.visualize(ast)
            dot_file = os.path.splitext(filename)[0] + ".dot"
            with open(dot_file, 'w') as f:
                f.write(dot_content)
            print(f"AST Visualization saved to: {dot_file}")
            print("Use 'dot -Tpng {0} -o {0}.png' to render image.".format(dot_file))
        
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
        if target == 'asm':
            codegen = AssemblyCodeGenerator(optimized_ir)
            generated_code = codegen.generate()
            target_name = "ASSEMBLY CODE"
        else:
            codegen = PythonCodeGenerator(optimized_ir)
            generated_code = codegen.generate()
            target_name = "GENERATED PYTHON CODE"
        
        if verbose:
            print("=" * 60)
            print(f"{target_name}:")
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
        print("Usage: python main.py <input_file.c> [output_file] [--asm] [--viz]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = None
    target = 'python'
    visualize = False
    
    # Parse args
    args = sys.argv[2:]
    for arg in args:
        if arg == '--asm':
            target = 'asm'
        elif arg == '--viz':
            visualize = True
        elif not arg.startswith('--'):
            output_file = arg
            
    if not output_file:
        ext = '.asm' if target == 'asm' else '.py'
        output_file = os.path.splitext(input_file)[0] + ext
    
    compile_file(input_file, output_file, target=target, visualize=visualize)

if __name__ == '__main__':
    main()
