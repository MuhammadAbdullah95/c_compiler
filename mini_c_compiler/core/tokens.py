from enum import Enum, auto

class TokenType(Enum):
    # Keywords
    INT = auto()
    FLOAT = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    RETURN = auto()
    PRINT = auto()

    # Identifiers and Literals
    IDENTIFIER = auto()
    NUMBER = auto()  # Integer
    FLOAT_NUMBER = auto() # Float

    # Operators
    PLUS = auto()       # +
    MINUS = auto()      # -
    STAR = auto()       # *
    SLASH = auto()      # /
    ASSIGN = auto()     # =
    
    # Comparison
    EQ = auto()         # ==
    NEQ = auto()        # !=
    GT = auto()         # >
    LT = auto()         # <
    GTE = auto()        # >=
    LTE = auto()        # <=

    # Delimiters
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    SEMICOLON = auto()  # ;
    COMMA = auto()      # ,

    EOF = auto()

class Token:
    def __init__(self, type: TokenType, value: any, line: int):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, Line:{self.line})"
