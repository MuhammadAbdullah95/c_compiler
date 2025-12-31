from mini_c_compiler.core.tokens import TokenType
from mini_c_compiler.core.errors import ParserError
from mini_c_compiler.core import ast_nodes as ast

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[0] if self.tokens else None

    def advance(self):
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None

    def peek(self):
        peek_pos = self.position + 1
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None

    def consume(self, token_type, error_message):
        if self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        else:
            raise ParserError(f"{error_message}. Found {self.current_token.type.name}", self.current_token.line)

    def parse(self):
        return self.program()

    def program(self):
        declarations = []
        while self.current_token.type != TokenType.EOF:
            declarations.append(self.declaration())
        return ast.Program(declarations)

    def declaration(self):
        # Look ahead to distinguish between var decl and func decl
        # Both start with Type Identifier
        # VarDecl: Type Identifier = ... ; or Type Identifier ;
        # FuncDecl: Type Identifier ( ... ) { ... }
        
        type_token = self.consume_type()
        name_token = self.consume(TokenType.IDENTIFIER, "Expected identifier")
        
        if self.current_token.type == TokenType.LPAREN:
            return self.func_decl(type_token, name_token)
        else:
            return self.var_decl(type_token, name_token)

    def consume_type(self):
        if self.current_token.type in (TokenType.INT, TokenType.FLOAT):
            token = self.current_token
            self.advance()
            return token
        else:
            raise ParserError("Expected type (int or float)", self.current_token.line)

    def var_decl(self, type_token, name_token):
        initializer = None
        if self.current_token.type == TokenType.ASSIGN:
            self.advance()
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';'")
        return ast.VarDecl(type_token.value, name_token.value, initializer)

    def func_decl(self, type_token, name_token):
        self.consume(TokenType.LPAREN, "Expected '('")
        params = []
        if self.current_token.type != TokenType.RPAREN:
            params = self.params()
        self.consume(TokenType.RPAREN, "Expected ')'")
        
        body = self.block()
        return ast.FuncDecl(type_token.value, name_token.value, params, body)

    def params(self):
        params = []
        params.append(self.param())
        while self.current_token.type == TokenType.COMMA:
            self.advance()
            params.append(self.param())
        return params

    def param(self):
        type_token = self.consume_type()
        name_token = self.consume(TokenType.IDENTIFIER, "Expected param name")
        return ast.Param(type_token.value, name_token.value)

    def block(self):
        self.consume(TokenType.LBRACE, "Expected '{'")
        statements = []
        while self.current_token.type != TokenType.RBRACE and self.current_token.type != TokenType.EOF:
            statements.append(self.statement())
        self.consume(TokenType.RBRACE, "Expected '}'")
        return ast.Block(statements)

    def statement(self):
        if self.current_token.type in (TokenType.INT, TokenType.FLOAT):
            type_token = self.current_token
            self.advance()
            name_token = self.consume(TokenType.IDENTIFIER, "Expected identifier")
            return self.var_decl(type_token, name_token)
        
        if self.current_token.type == TokenType.IF:
            return self.if_stmt()
        
        if self.current_token.type == TokenType.WHILE:
            return self.while_stmt()
        
        if self.current_token.type == TokenType.RETURN:
            return self.return_stmt()
        
        if self.current_token.type == TokenType.PRINT:
            return self.print_stmt()
        
        if self.current_token.type == TokenType.LBRACE:
            return self.block()

        # Assignment or Expression Statement (but we only support Assignment as stmt for now, or just expression?)
        # The grammar says: assignment ';'
        # assignment -> IDENTIFIER '=' expression
        
        if self.current_token.type == TokenType.IDENTIFIER:
            # Check if it's assignment or function call
            name_token = self.current_token
            self.advance()
            
            if self.current_token.type == TokenType.ASSIGN:
                self.advance()
                expr = self.expression()
                self.consume(TokenType.SEMICOLON, "Expected ';'")
                return ast.Assignment(name_token.value, expr)
            
            elif self.current_token.type == TokenType.LPAREN:
                # Function call statement
                # We need to parse it as an expression (FunctionCall), then consume semicolon
                # We can reuse primary() logic but we already consumed identifier
                
                self.advance() # consume '('
                args = []
                if self.current_token.type != TokenType.RPAREN:
                    args = self.arguments()
                self.consume(TokenType.RPAREN, "Expected ')'")
                self.consume(TokenType.SEMICOLON, "Expected ';'")
                
                return ast.ExpressionStmt(ast.FunctionCall(name_token.value, args))


        raise ParserError(f"Unexpected token {self.current_token.type}", self.current_token.line)

    def if_stmt(self):
        self.consume(TokenType.IF, "Expected 'if'")
        self.consume(TokenType.LPAREN, "Expected '('")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Expected ')'")
        then_branch = self.block()
        else_branch = None
        if self.current_token.type == TokenType.ELSE:
            self.advance()
            else_branch = self.block()
        return ast.IfStmt(condition, then_branch, else_branch)

    def while_stmt(self):
        self.consume(TokenType.WHILE, "Expected 'while'")
        self.consume(TokenType.LPAREN, "Expected '('")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Expected ')'")
        body = self.block()
        return ast.WhileStmt(condition, body)

    def return_stmt(self):
        self.consume(TokenType.RETURN, "Expected 'return'")
        value = None
        if self.current_token.type != TokenType.SEMICOLON:
            value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';'")
        return ast.ReturnStmt(value)

    def print_stmt(self):
        self.consume(TokenType.PRINT, "Expected 'print'")
        self.consume(TokenType.LPAREN, "Expected '('")
        expr = self.expression()
        self.consume(TokenType.RPAREN, "Expected ')'")
        self.consume(TokenType.SEMICOLON, "Expected ';'")
        return ast.PrintStmt(expr)

    def expression(self):
        return self.equality()

    def equality(self):
        node = self.comparison()
        while self.current_token.type in (TokenType.EQ, TokenType.NEQ):
            op = self.current_token.value
            self.advance()
            right = self.comparison()
            node = ast.BinaryOp(node, op, right)
        return node

    def comparison(self):
        node = self.term()
        while self.current_token.type in (TokenType.GT, TokenType.LT, TokenType.GTE, TokenType.LTE):
            op = self.current_token.value
            self.advance()
            right = self.term()
            node = ast.BinaryOp(node, op, right)
        return node

    def term(self):
        node = self.factor()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token.value
            self.advance()
            right = self.factor()
            node = ast.BinaryOp(node, op, right)
        return node

    def factor(self):
        node = self.unary()
        while self.current_token.type in (TokenType.STAR, TokenType.SLASH):
            op = self.current_token.value
            self.advance()
            right = self.unary()
            node = ast.BinaryOp(node, op, right)
        return node

    def unary(self):
        if self.current_token.type == TokenType.MINUS:
            op = self.current_token.value
            self.advance()
            return ast.UnaryOp(op, self.unary())
        return self.primary()

    def primary(self):
        if self.current_token.type == TokenType.NUMBER:
            token = self.current_token
            self.advance()
            return ast.Number(token.value)
        
        if self.current_token.type == TokenType.FLOAT_NUMBER:
            token = self.current_token
            self.advance()
            return ast.FloatNumber(token.value)
        
        if self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.advance()
            if self.current_token.type == TokenType.LPAREN:
                # Function call
                self.advance()
                args = []
                if self.current_token.type != TokenType.RPAREN:
                    args = self.arguments()
                self.consume(TokenType.RPAREN, "Expected ')'")
                return ast.FunctionCall(name, args)
            return ast.Identifier(name)
        
        if self.current_token.type == TokenType.LPAREN:
            self.advance()
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expected ')'")
            return expr
        
        raise ParserError(f"Unexpected token {self.current_token.type}", self.current_token.line)

    def arguments(self):
        args = []
        args.append(self.expression())
        while self.current_token.type == TokenType.COMMA:
            self.advance()
            args.append(self.expression())
        return args
