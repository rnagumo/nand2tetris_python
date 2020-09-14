
from typing import List


class JackTokenizer:
    """Tokenizer for Jack lang."""

    # Token
    t_invalid = 0
    t_keyword = 1
    t_symbol = 2
    t_integer_const = 3
    t_string_const = 4
    t_identifier = 5

    xml_tag_table = {
        1: "keyword",
        2: "symbol",
        3: "integerConstant",
        4: "stringConstant",
        5: "identifier",
    }

    # Template
    keyword = ["class", "constructor", "function", "method", "field", "static",
               "var", "int", "char", "boolean", "void", "true", "false",
               "null", "this", "let", "do", "if", "else", "while", "return"]
    symbol = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/",
              "&", "|", "<", ">", "=", "~"]
    int_lim = (0, 32767)

    # Tokenize for XML
    xml_table = {"<": "&lt;", ">": "&gt;", "&": "&amp;"}

    def __init__(self):

        self._code: List[str] = []
        self._row_num = 0
        self._column_num = 0
        self._row = 0
        self._column = 0
        self._current_line = ""
        self._current_token = ""
        self._in_comment = False

    @property
    def current_token(self) -> str:
        res = self._current_token.strip('"')
        if res in self.xml_table:
            res = self.xml_table[res]
        return res

    @property
    def current_xml(self) -> str:
        if self.token_type == self.t_invalid:
            return ""

        tag = self.xml_tag_table[self.token_type]
        return f"<{tag}> {self.current_token} </{tag}>"

    @property
    def code(self) -> List[str]:
        return self._code

    @code.setter
    def code(self, code: List[str]) -> None:
        self._code = code
        self._row_num = len(code)
        self._column_num = len(code[0]) if code[0] else 0
        self._row = 0
        self._column = 100

    def has_more_token(self) -> bool:
        """Boolean flag for more token.

        Returns:
            has (bool): Token existence.
        """

        return self._row < self._row_num or self._column < self._column_num

    def _not_end_line(self) -> bool:
        return self._column < self._column_num

    def advance(self) -> None:
        """Go to the next token.

        Raises:
            RuntimeError: If `has_more_token` is `False`.
        """

        if not self.has_more_token():
            raise RuntimeError("No successive token exists.")

        self._current_token = ""

        # End of line, go to next row
        if self._column >= self._column_num:
            self._current_line = self._code[self._row].split("//")[0].strip()
            self._column_num = len(self._current_line)
            self._row += 1
            self._column = 0

        if self._column_num == 0:
            return

        # Start of comment
        if self._column_num >= 2 and self._current_line[:2] == "/*":
            self._in_comment = True

        # End of comment
        if (self._in_comment
                and self._current_line[self._column:self._column + 2] == "*/"):
            self._column += 2
            self._in_comment = False

        # Middle of comment
        if self._in_comment:
            self._column += 1
            return

        # Skip spaces
        while (self._not_end_line()
                and self._current_line[self._column] == " "):
            self._column += 1

        # One-word symbol
        if (self._not_end_line()
                and self._current_line[self._column] in self.symbol):
            self._current_token = self._current_line[self._column]
            self._column += 1
            return

        # String in double quotation
        if self._not_end_line() and self._current_line[self._column] == '"':
            token = '"'
            self._column += 1
            while not self._current_line[self._column] == '"':
                token += self._current_line[self._column]
                self._column += 1
            token += '"'
            self._current_token = token
            self._column += 1
            return

        # Multiple-words symbol
        token = ""
        while self._not_end_line():
            if (self._current_line[self._column] == " "
                    or self._current_line[self._column] in self.symbol):
                break

            token += self._current_line[self._column]
            self._column += 1
        self._current_token = token

    @property
    def token_type(self) -> int:
        """Token type.

        Returns:
            token_type (int): parsed current token type.

        Raises:
            ValueErorr: If unexpected token is given.
        """

        if not self._current_token:
            return self.t_invalid

        if self._current_token in self.keyword:
            return self.t_keyword
        elif self._current_token in self.symbol:
            return self.t_symbol
        elif self._is_all_numeric():
            return self.t_integer_const
        elif self._is_string_const():
            return self.t_string_const
        elif self._is_valid_identifier():
            return self.t_identifier

        raise ValueError(f"Unexpected token: {self._current_token}")

    def is_keyword(self) -> bool:
        return self.token_type == self.t_keyword

    def is_symbol(self) -> bool:
        return self.token_type == self.t_symbol

    def is_integer(self) -> bool:
        return self.token_type == self.t_integer_const

    def is_string(self) -> bool:
        return self.token_type == self.t_string_const

    def is_identifier(self) -> bool:
        return self.token_type == self.t_identifier

    def _is_all_numeric(self) -> bool:
        return (
            all("0" <= c <= "9" for c in self._current_token) and
            (self.int_lim[0] <= int(self._current_token) <= self.int_lim[1]))

    def _is_string_const(self) -> bool:
        return self._current_token[0] == self._current_token[-1] == '"'

    def _is_valid_identifier(self) -> bool:
        return all(
            "0" <= c <= "9" or "A" <= c <= "Z" or "a" <= c <= "z" or c == "_"
            for c in self._current_token)
