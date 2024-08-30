from utils.token_type import TokenType
from lexical.token import Token

import re  

class Scanner:
    def __init__(self, source):
        self.position = 0
        self.row = 1
        self.column = 1
        self.source_buffer = self.read_source(source)
        self.reserved_words = {
            "int": TokenType.INT,
            "float": TokenType.FLOAT,
            "print": TokenType.PRINT,
            "if": TokenType.IF,
            "else": TokenType.ELSE
        }
        self.invalid_chars = {'@', '`', '¨', '~', '¨', '­', '´', '·', '¸' }
        self.accented_char_pattern = re.compile(r'[áàâãéèêíïóôõöúüç]')
        self.stack = []

    def read_source(self, source):
        with open(source, 'r') as file:
            return file.read()

    def next_token(self):
        state = 0
        content = ""
        
        while True:
            if self.is_eof():
                if self.stack:
                    unclosed = ''.join(token[0] for token in self.stack)
                    self.error(f"Tokens não fechados: {unclosed}", self.stack[-1][1], self.stack[-1][2])
                if state != 0:
                    return self.finalize_token(state, content)
                return None

            current_char = self.next_char()
            
            if self.accented_char_pattern.match(current_char):
                if state not in [11, 12]: 
                    self.error(f"Caractere inválido fora de string: {current_char}", self.row, self.column)
            
            if current_char in self.invalid_chars:
                self.error(f"Caractere inválido: {current_char}", self.row, self.column)
            
            if state == 0:
                if self.is_space(current_char):
                    continue 
                elif current_char == '#':
                    self.skip_comment()
                elif self.is_valid_identifier_start(current_char):
                    content += current_char
                    state = 1
                elif self.is_digit_or_dot(current_char):
                    content += current_char
                    state = 3 if current_char != '.' else 5
                elif self.is_operator(current_char):
                    content += current_char
                    state = 9 
                elif current_char in '><!':
                    content += current_char
                    state = 8
                elif current_char == '(':
                    self.stack.append(('(', self.row, self.column))
                    content += current_char
                    state = 10  
                elif current_char == ')':
                    if self.stack and self.stack[-1][0] == '(':
                        self.stack.pop()
                    else:
                        self.error("Parêntese de fechamento não correspondente", self.row, self.column)
                    return Token(TokenType.PARENTHESIS, current_char)
                elif current_char == '{':
                    self.stack.append(('{', self.row, self.column))
                    return Token(TokenType.LEFT_BRACE, current_char)
                elif current_char == '}':
                    if self.stack and self.stack[-1][0] == '{':
                        self.stack.pop()
                    else:
                        self.error("Chave de fechamento não correspondente", self.row, self.column)
                    return Token(TokenType.RIGHT_BRACE, current_char)
                elif current_char == '"':
                    state = 11
                elif current_char == "'":
                    state = 12
                else:
                    self.error(f"Caractere inválido: {current_char}", self.row, self.column)
            elif state == 1:
                if self.is_valid_identifier_char(current_char):
                    content += current_char
                else:
                    self.back()
                    return self.resolve_identifier_or_reserved(content)
            elif state == 3:
                if current_char.isdigit():
                    content += current_char
                elif current_char == '.':
                    content += current_char
                    state = 4
                else:
                    self.back()
                    return Token(TokenType.NUMBER, content)
            elif state == 4:
                if current_char.isdigit():
                    content += current_char
                    state = 6
                else:
                    self.error(f"Número malformado: {content}", self.row, self.column)
            elif state == 5:
                if current_char.isdigit():
                    content += current_char
                    state = 6
                else:
                    self.error(f"Número malformado: {content}", self.row, self.column)
            elif state == 6:
                if current_char.isdigit():
                    content += current_char
                else:
                    self.back()
                    return Token(TokenType.NUMBER, content)
            elif state == 8:
                if current_char == '=':
                    content += current_char
                else:
                    self.back()
                return self.resolve_operator(content)
            elif state == 9:
                if current_char == '=':
                    content += current_char
                    return self.resolve_operator(content)
                else:
                    self.back()
                    return self.resolve_operator(content)
            elif state == 10:
                if current_char == ')':
                    content += current_char
                    return Token(TokenType.PARENTHESIS, content)
                else:
                    self.back()
                    return Token(TokenType.PARENTHESIS, '(')
            elif state == 11:  
                if current_char == '"':
                    return Token(TokenType.STRING, content)
                elif self.is_eof():
                    self.error(f"String não fechada: {content}", self.row, self.column)
                else:
                    content += current_char
            elif state == 12:  
                if current_char == "'":
                    return Token(TokenType.STRING, content)
                elif self.is_eof():
                    self.error(f"String não fechada: {content}", self.row, self.column)
                else:
                    content += current_char

    def finalize_token(self, state, content):
        if state == 1:
            return self.resolve_identifier_or_reserved(content)
        elif state == 3 or state == 6:
            return Token(TokenType.NUMBER, content)
        elif state == 8 or state == 9:
            return self.resolve_operator(content)
        self.error(f"Fim inesperado da entrada: {content}", self.row, self.column)

    def resolve_identifier_or_reserved(self, content):
        if content in self.reserved_words:
            return Token(self.reserved_words[content], content)
        else:
            return Token(TokenType.IDENTIFIER, content)

    def resolve_operator(self, content):
        if content in {'+', '-', '*', '/', '=', '==', '!=', '>', '<', '>=', '<='}:
            return Token(TokenType.OPERATOR, content)
        self.error(f"Operador inválido: {content}", self.row, self.column)

    def is_space(self, c):
        return c in ' \n\t\r'

    def is_eof(self):
        return self.position >= len(self.source_buffer)

    def next_char(self):
        if not self.is_eof():
            char = self.source_buffer[self.position]
            self.position += 1
            if char == '\n':
                self.row += 1
                self.column = 0
            self.column += 1
            return char

    def back(self):
        self.position -= 1
        if self.source_buffer[self.position] == '\n':
            self.row -= 1
            self.column = self.find_previous_column()
        else:
            self.column -= 1

    def find_previous_column(self):
        line_start = self.source_buffer.rfind('\n', 0, self.position) + 1
        return self.position - line_start + 1

    def skip_comment(self):
        while not self.is_eof():
            current_char = self.next_char()
            if current_char in '\n\r':
                break

    def error(self, message, row, column):
        raise Exception(f"{message} na linha {row}, coluna {column - 1}")

    def is_valid_identifier_start(self, c):
        return c.isalpha() or c == '_'

    def is_valid_identifier_char(self, c):
        return c.isalnum() or c == '_'

    def is_digit_or_dot(self, c):
        return c.isdigit() or c == '.'

    def is_operator(self, c):
        return c in '+-*/='