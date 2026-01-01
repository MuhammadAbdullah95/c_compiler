# 🚀 Mini C Compiler - Startup Guide

This guide provides instructions on how to set up and run the Mini C Compiler on your machine.

## 📋 Prerequisites
*   **Python 3.8+** must be installed.
*   (Optional) **Graphviz** is needed only if you want to generate AST visualizations.

## 🏃‍♂️ Quick Start

The compiler is run from the root directory using the `python -m` syntax.

### 1. Basic Compilation (Transpile to Python)
This helps you quickly check if the C code logic is correct by converting it to Python.
```bash
python -m mini_c_compiler.main mini_c_compiler/examples/test1.c
```
*   **Output:** Generates `test1.py` and runs it.

---

### 2. Compile to Assembly (`.asm`) 🛠️
This is the **core feature** of the project. It behaves like a real compiler, generating low-level instructions.
```bash
python -m mini_c_compiler.main mini_c_compiler/examples/test2.c --asm
```
*   **Output:** Generates `mini_c_compiler/examples/test2.asm`

---

### 3. Run the Virtual Machine (VM) 🖥️
Once you have the `.asm` file, you execute it using the custom Stack VM.
```bash
python -m mini_c_compiler.vm mini_c_compiler/examples/test2.asm
```
*   **Output:** The result of your program (e.g., `120`).

---

### 4. Visualize the AST 🌳
To see the internal tree structure of your code:
```bash
python -m mini_c_compiler.main mini_c_compiler/examples/test1.c --viz
```
*   **Output:** Generates `test1.dot`.
*   **Render it:** You can open this file in any Graphviz viewer or convert it to PNG:
    ```bash
    dot -Tpng test1.dot -o test1.png
    ```

## 🧪 Included Test Files
You can find these in `mini_c_compiler/examples/`:

*   `test1.c`: Simple math and function calls.
*   `test2.c`: Loops (`while`) and factorials.
*   `test_opt.c`: Demonstrates optimization (Constant Propagation).
*   `error_test.c`: Demonstrates Semantic Error handling (will fail to compile).
