
# ✅ **FULL IMPLEMENTATION PLAN: Mini C Compiler in Python (C Subset)**

**Purpose:** Build a working compiler that takes simplified **C language** as input and outputs **Intermediate Representation (TAC)** and **executed Python code** or **custom assembly**.

---

# 🟦 **PROJECT OVERVIEW**

The compiler must follow these stages:

1. **Lexical Analysis** → Token Stream
2. **Syntax Analysis** → AST
3. **Semantic Analysis** → Symbol Table + Type Checks
4. **Intermediate Representation (IR)** → Three-Address Code
5. **Optimization** → Constant Folding, Dead-Code Elimination
6. **Code Generation** → Python Code OR Custom Assembly

---

# 🗂️ **FOLDER + FILE STRUCTURE**

Create this exact structure:

```
mini_c_compiler/
│
├── main.py
├── lexer.py
├── parser.py
├── semantic.py
├── ir.py
├── optimizer.py
├── codegen.py
│
├── core/
│   ├── tokens.py
│   ├── ast_nodes.py
│   ├── errors.py
│   └── symbol_table.py
│
├── examples/
│   ├── test1.c
│   └── test2.c
│
└── tests/
    ├── test_lexer.py
    ├── test_parser.py
    ├── test_semantic.py
    ├── test_ir.py
    └── test_codegen.py
```

---

# 🎯 **LANGUAGE SUBSET TO SUPPORT**

The compiler should support:

### ✔ Data Types

* `int`, `float`

### ✔ Operators

* `+`, `-`, `*`, `/`
* `==`, `!=`, `>`, `<`, `>=`, `<=`

### ✔ Control Flow

* `if`, `else`
* `while`

### ✔ Statements

* variable declaration
* assignment
* print function
* return statements
* simple functions

### ✘ Excluded (to avoid complexity)

* pointers
* arrays
* structs
* dynamic memory
* preprocessor

---

# 🟦 **STAGE 1 — LEXICAL ANALYZER (lexer.py)**

### Objective

Convert input C code into a list of **Token** objects.

### Requirements

Define token types:

```
KEYWORD, IDENTIFIER, NUMBER, FLOAT,
PLUS, MINUS, STAR, SLASH,
LPAREN, RPAREN, LBRACE, RBRACE,
ASSIGN, SEMICOLON,
EQ, NEQ, GT, LT, GTE, LTE
```

### Lexer Tasks

1. Define token types in `core/tokens.py`.
2. Implement regex rules using Python `re`.
3. Skip whitespace and newlines.
4. Produce tokens with:

   * type
   * value
   * line number

### Output Example for:

```c
int x = 5 + 2;
```

```
[KEYWORD(int), IDENTIFIER(x), ASSIGN, NUMBER(5), PLUS, NUMBER(2), SEMICOLON]
```

### Acceptance Criteria

* Handles errors on unknown characters
* Provides correct token positions
* All tokens match the grammar

---

# 🟩 **STAGE 2 — SYNTAX ANALYZER (parser.py)**

### Objective

Convert token stream → **AST (Abstract Syntax Tree)**

### Parsing Method

Use **Recursive Descent Parsing**.

### Grammar (AI-Agent Friendly)

```
program        → declaration_list

declaration_list → declaration declaration_list | ε

declaration    → var_decl | func_decl

var_decl       → type IDENTIFIER (‘=’ expression)? ‘;’

type           → 'int' | 'float'

func_decl      → type IDENTIFIER '(' params ')' block

params         → param (',' param)* | ε

param          → type IDENTIFIER

block          → '{' statement_list '}'

statement_list → statement statement_list | ε

statement      → var_decl 
               | assignment ';'
               | if_stmt
               | while_stmt
               | return_stmt ';'
               | print_stmt ';'

assignment     → IDENTIFIER '=' expression

if_stmt        → 'if' '(' expression ')' block ('else' block)?

while_stmt     → 'while' '(' expression ')' block

print_stmt     → 'print' '(' expression ')'

expression     → equality

equality       → comparison (( '==' | '!=' ) comparison)*

comparison     → term (( '>' | '<' | '>=' | '<=' ) term)*

term           → factor (( '+' | '-' ) factor)*

factor         → unary (( '*' | '/' ) unary)*

unary          → ( '-' ) unary | primary

primary        → NUMBER | IDENTIFIER | '(' expression ')'
```

### Acceptance Criteria

* Should build AST classes from `core/ast_nodes.py`
* Should reject invalid syntax with clear errors
* Should support nested blocks

---

# 🟨 **STAGE 3 — SEMANTIC ANALYSIS (semantic.py)**

### Objective

Check logical correctness and build a **Symbol Table**.

### Tasks for AI Agent

1. Build symbol table class in `core/symbol_table.py`.
2. Handle variable declarations.
3. Track scopes using a stack.
4. Check for:

   * redeclaration
   * use before declaration
   * mismatched types
   * return type mismatch
   * function signature validation

### Acceptance Criteria

* Records variable types + scope
* Emits semantic errors in correct line number
* Rejects code like:

```c
int x;
float x;  // error: redeclaration
```

---

# 🟧 **STAGE 4 — IR GENERATION (ir.py)**

### Objective

Generate **Three-Address Code (TAC)**.

### TAC Format

```
t1 = 5 + 10
x = t1
```

### Required IR Instructions

* Assignment
* Binary ops
* Unary ops
* Conditional jumps
* Labels
* Function calls
* Return
* Print

### IR Examples

#### For:

```c
x = a + b * 5;
```

Output:

```
t1 = b * 5
t2 = a + t1
x = t2
```

### Control Flow

#### If:

```
if x > 5 { print(x); }
```

Translate to:

```
t1 = x > 5
IF_FALSE t1 GOTO L1
PRINT x
L1:
```

### Acceptance Criteria

* Every AST node should have an IR generator function
* No missing labels
* No undefined temporaries

---

# 🟥 **STAGE 5 — OPTIMIZER (optimizer.py)**

### Required Optimizations

✔ Constant Folding

```
t1 = 5 + 10 → t1 = 15
```

✔ Dead Code Elimination
Remove instructions whose results are not used.

✔ Strength Reduction (optional)

```
x * 2 → x << 1
```

### Acceptance Criteria

* IR must stay semantically identical
* Must not remove side-effects (print, return, etc.)

---

# 🟪 **STAGE 6 — CODE GENERATION (codegen.py)**

Choosing **one** output backend:

---

## Option A — Generate Python code (simple & runnable)

Example TAC:

```
t1 = 15
x = t1
print(x)
```

Output:

```python
t1 = 15
x = t1
print(x)
```

---

## Option B — Generate Custom Assembly (for marks)

Example:

```
LOAD 15
STORE t1
STORE x, t1
PRINT x
```

---

### Acceptance Criteria

* Must convert TAC to final code
* Must support variables and control flow
* Must run without errors

---

# 🎛 **main.py Requirements**

`main.py` should:

1. Read `.c` file
2. Pass through all compiler stages
3. Print intermediate outputs:

```
TOKENS:
AST:
SEMANTIC CHECK:
IR:
OPTIMIZED IR:
GENERATED CODE:
```

4. Optionally execute generated code

---

# 🧪 **TESTING REQUIREMENTS**

### Lexer Tests

* Keywords
* Numbers
* Identifiers
* Operators
* Invalid characters

### Parser Tests

* Valid grammar
* Invalid syntax

### Semantic Tests

* undeclared var
* type mismatch
* correct scope handling

### IR Tests

* Correct TAC for sample inputs

### Codegen Tests

* Output runs correctly

---

# ⭐ **EXAMPLE INPUT PROGRAM (Supported by Compiler)**

Save as `examples/test1.c`:

```c
int x = 5;
int y = 10;

int add(int a, int b) {
    return a + b;
}

int main() {
    int z = add(x, y);
    if (z > 10) {
        print(z);
    }
}
```

---



