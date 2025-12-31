import re
from mini_c_compiler.core.tokens import Token, TokenType
from mini_c_compiler.core.errors import LexerError

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.current_char = self.source_code[0] if self.source_code else None

    def advance(self):
        self.position += 1
        if self.position < len(self.source_code):
            self.current_char = self.source_code[self.position]
        else:
            self.current_char = None

    def peek(self):
        peek_pos = self.position + 1
        if peek_pos < len(self.source_code):
            return self.source_code[peek_pos]
        return None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            if self.current_char == '\n':
                self.line += 1
            self.advance()

    def _number(self):
        result = ''
        is_float = False
        
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if is_float:
                    break # Second dot
                is_float = True
            result += self.current_char
            self.advance()

        if is_float:
            return Token(TokenType.FLOAT_NUMBER, float(result), self.line)
        else:
            return Token(TokenType.NUMBER, int(result), self.line)

    def _identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        keywords = {
            'int': TokenType.INT,
            'float': TokenType.FLOAT,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'return': TokenType.RETURN,
            'print': TokenType.PRINT
        }

        token_type = keywords.get(result, TokenType.IDENTIFIER)
        return Token(token_type, result, self.line)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalpha() or self.current_char == '_':
                return self._identifier()

            if self.current_char.isdigit():
                return self._number()

            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+', self.line)
            
            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-', self.line)
            
            if self.current_char == '*':
                self.advance()
                return Token(TokenType.STAR, '*', self.line)
            
            if self.current_char == '/':
                self.advance()
                return Token(TokenType.SLASH, '/', self.line)
            
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', self.line)
            
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', self.line)
            
            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LBRACE, '{', self.line)
            
            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RBRACE, '}', self.line)
            
            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';', self.line)
            
            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',', self.line)

            if self.current_char == '=':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.EQ, '==', self.line)
                self.advance()
                return Token(TokenType.ASSIGN, '=', self.line)

            if self.current_char == '!':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.NEQ, '!=', self.line)
                raise LexerError(f"Unexpected character '!'", self.line)

            if self.current_char == '>':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.GTE, '>=', self.line)
                self.advance()
                return Token(TokenType.GT, '>', self.line)

            if self.current_char == '<':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.LTE, '<=', self.line)
                self.advance()
                return Token(TokenType.LT, '<', self.line)

            raise LexerError(f"Unexpected character '{self.current_char}'", self.line)

        return Token(TokenType.EOF, None, self.line)

    def tokenize(self):
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens
