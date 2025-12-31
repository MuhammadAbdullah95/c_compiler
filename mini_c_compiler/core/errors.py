class CompilerError(Exception):
    def __init__(self, message, line):
        self.message = message
        self.line = line
        super().__init__(f"Line {line}: {message}")

class LexerError(CompilerError):
    pass

class ParserError(CompilerError):
    pass

class SemanticError(CompilerError):
    pass
