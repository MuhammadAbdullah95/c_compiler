import unittest
from mini_c_compiler.lexer import Lexer
from mini_c_compiler.core.tokens import TokenType, Token
from mini_c_compiler.core.errors import LexerError

class TestLexer(unittest.TestCase):
    def test_basic_tokens(self):
        code = "int x = 5;"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.INT,
            TokenType.IDENTIFIER,
            TokenType.ASSIGN,
            TokenType.NUMBER,
            TokenType.SEMICOLON,
            TokenType.EOF
        ]
        
        self.assertEqual(len(tokens), len(expected_types))
        for i, token in enumerate(tokens):
            self.assertEqual(token.type, expected_types[i])
        
        self.assertEqual(tokens[1].value, 'x')
        self.assertEqual(tokens[3].value, 5)

    def test_operators(self):
        code = "+ - * / == != > < >= <="
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH,
            TokenType.EQ, TokenType.NEQ, TokenType.GT, TokenType.LT,
            TokenType.GTE, TokenType.LTE, TokenType.EOF
        ]
        
        self.assertEqual(len(tokens), len(expected_types))
        for i, token in enumerate(tokens):
            self.assertEqual(token.type, expected_types[i])

    def test_keywords(self):
        code = "if else while return print"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.IF, TokenType.ELSE, TokenType.WHILE, 
            TokenType.RETURN, TokenType.PRINT, TokenType.EOF
        ]
        
        self.assertEqual(len(tokens), len(expected_types))
        for i, token in enumerate(tokens):
            self.assertEqual(token.type, expected_types[i])

    def test_numbers(self):
        code = "123 45.67"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].value, 123)
        
        self.assertEqual(tokens[1].type, TokenType.FLOAT_NUMBER)
        self.assertEqual(tokens[1].value, 45.67)

    def test_braces_parens(self):
        code = "(){}"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.LPAREN, TokenType.RPAREN, 
            TokenType.LBRACE, TokenType.RBRACE, TokenType.EOF
        ]
        
        for i, token in enumerate(tokens):
            self.assertEqual(token.type, expected_types[i])

    def test_error(self):
        code = "@"
        lexer = Lexer(code)
        with self.assertRaises(LexerError):
            lexer.tokenize()

    def test_complex_expression(self):
        code = "int res = (a + b) * 10;"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.INT, TokenType.IDENTIFIER, TokenType.ASSIGN,
            TokenType.LPAREN, TokenType.IDENTIFIER, TokenType.PLUS, TokenType.IDENTIFIER, TokenType.RPAREN,
            TokenType.STAR, TokenType.NUMBER, TokenType.SEMICOLON, TokenType.EOF
        ]
        
        self.assertEqual(len(tokens), len(expected_types))
        for i, token in enumerate(tokens):
            self.assertEqual(token.type, expected_types[i])

if __name__ == '__main__':
    unittest.main()
