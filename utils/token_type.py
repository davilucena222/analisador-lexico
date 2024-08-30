from enum import Enum, auto

class TokenType(Enum):
    IDENTIFIER = auto()
    NUMBER = auto()
    OPERATOR = auto()
    PARENTHESIS = auto()
    INT = auto()
    FLOAT = auto()
    PRINT = auto()
    IF = auto()
    ELSE = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    STRING = auto() 