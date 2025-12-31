from dataclasses import dataclass
from typing import Dict, Optional, List

@dataclass
class Symbol:
    name: str
    type_name: str
    category: str # 'var' or 'func'
    params: Optional[List[str]] = None # For functions: list of param types

class SymbolTable:
    def __init__(self, parent=None):
        self.symbols: Dict[str, Symbol] = {}
        self.parent: Optional[SymbolTable] = parent

    def define(self, symbol: Symbol):
        self.symbols[symbol.name] = symbol

    def lookup(self, name: str, current_scope_only=False) -> Optional[Symbol]:
        symbol = self.symbols.get(name)
        if symbol:
            return symbol
        if current_scope_only:
            return None
        if self.parent:
            return self.parent.lookup(name)
        return None
