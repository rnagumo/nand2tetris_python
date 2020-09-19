
from typing import List, Union, Tuple, Deque

import collections
import dataclasses

from nnttpy import jackcompiler


@dataclasses.dataclass
class SymbolAttr:
    class_name: str = ""
    sub_class: str = ""
    category: str = ""
    type: str = ""
    kind: str = ""


class JackCompileEngine(jackcompiler.XMLCompilationEngine):
    """Symbol engine with symbol table."""

    category_list = [
        "static", "field", "argument", "var", "class", "subroutine"]
    kind_list = ["static", "field", "argument", "var"]

    ops_table = {
        "+": "add",
        "-": "sub",
        "=": "eq",
        "&lt;": "<",
        "&gt;": ">",
        "&amp;": "and",
        "|": "or",
    }
    unary_ops_table = {
        "-": "neg",
        "~": "not",
    }

    def __init__(self):
        super().__init__()

        self._symbol_table = jackcompiler.SymbolTable()
        self._symbol_attr = SymbolAttr()
        self._writer = jackcompiler.VMWriter()
        self._is_defined = False
        self._buffer: Deque[Tuple[str, str]] = collections.deque()

    def compile(self, token_list: List[Tuple[int, str]]) -> List[str]:
        """Compiles given token list.

        Caution: This method should be called first.

        Args:
            token_list (list of [int, str]): List of line number and tokens
                ('<tag> content </tag>').

        Returns:
            code_list (list of str): Compiled codes.
        """

        super().compile(token_list)

        return self._writer.code[:]

    def compile_class(self) -> None:
        """Compiles class.

        'class' className '{' classVarDec* subroutineDec* '}'
        """

        self._symbol_table.start_class()
        self._symbol_attr.category = "class"
        self._symbol_attr.kind = ""
        self._symbol_attr.class_name = ""
        self._symbol_attr.sub_class = ""
        self._is_defined = True
        super().compile_class()
        self._is_defined = False

    def compile_subroutine(self) -> None:
        """Compiles subroutine.

        ('constructor'|'function'|'method') ('void'|type) subroutineName
        '(' parameterList ')' subroutineBody
        """

        self._symbol_table.start_subroutine()
        self._symbol_attr.category = "subroutine"
        self._symbol_attr.kind = ""
        self._is_defined = True
        self._buffer.clear()

        self._write_non_terminal_tag("subroutineDec")

        # ('constructor'|'function'|'method')
        self._write_checked_token("keyword", self.subroutine_tokens)

        # ('void'|type) subroutineName
        self._write_checked_type(allow_void=True)
        self._write_checked_token("identifier", dec="subroutine")

        # '(' parameterList ')' subroutineBody
        self._write_checked_token("symbol", "(")
        self.compile_parameter_list()
        self._write_checked_token("symbol", ")")

        _, name = self._buffer.popleft()
        n_locals = 0
        while self._buffer:
            kind, _ = self._buffer.popleft()
            n_locals += int(kind == "var")
        self._writer.write_function(name, n_locals)

        # subroutineBody
        self.compile_subroutine_body()
        self._write_non_terminal_tag("/subroutineDec")

        self._is_defined = False

    def compile_parameter_list(self) -> None:
        """Compiles parameter list.

        ((type varName) (',' type varName)*)?
        """

        self._symbol_attr.category = "argument"
        self._symbol_attr.kind = "argument"
        self._is_defined = True
        super().compile_parameter_list()
        self._is_defined = False

    def compile_var_dec(self) -> None:
        """Compiles variable declaration.

        'var' type varName (',' varName)* ';'
        """

        self._symbol_attr.category = "var"
        self._symbol_attr.kind = "var"
        self._is_defined = True
        super().compile_var_dec()
        self._is_defined = False

    def compile_let(self) -> None:
        """Compiles let statement.

        'let' varName ('[' expression ']')? '=' expression ';'
        """

        self._buffer.clear()

        # 'let' varName
        self._write_non_terminal_tag("letStatement")
        self._write_checked_token("keyword", "let")
        self._write_checked_token("identifier", dec="var")
        operand1 = self._buffer.popleft()

        # ('[' expression ']')?
        array_assingment = self._check_syntax("symbol", "[")
        if array_assingment:
            self._write_checked_token("symbol", "[")
            self.compile_expression()
            self._write_checked_token("symbol", "]")

            ptr = self._buffer.popleft()
            element = self._symbol_table[ptr]
            self._writer.write_push(element.kind, element.number)

        # '='
        self._write_checked_token("symbol", "=")
        self._buffer.popleft()

        # expression ';'
        self.compile_expression()
        self._write_checked_token("symbol", ";")
        self._write_non_terminal_tag("/letStatement")

        if not array_assingment:
            element = self._symbol_table[operand1]
            self._writer.write_pop(element.kind, element.number)
        else:
            self._writer.write_pop("temp", 0)
            self._writer.write_pop("pointer", 1)
            self._writer.write_push("temp", 0)
            self._writer.write_pop("that", 0)

    def compile_return(self) -> None:
        """Compiles return statement.

        'return' expression? ';'
        """

        self._write_non_terminal_tag("returnStatement")
        self._write_checked_token("keyword", "return")
        if self._check_syntax("symbol", ";"):
            # Write dummy constant for 'void' returned value
            self._writer.write_push("constant", "0")
        else:
            self.compile_expression()
        self._write_checked_token("symbol", ";")

        self._writer.write_return()
        self._write_non_terminal_tag("/returnStatement")

    def compile_subroutine_call(self) -> None:
        """Compiles subroutine call.

        subroutineName '(' expressionList ')' |
        (className|varName) '.' subroutineName '(' expressionList ')'
        """

        self._buffer.clear()
        super().compile_subroutine_call()

        # Subroutine name
        kind, name = self._buffer.popleft()
        if kind != "subroutine":
            kind, name = self._buffer.popleft()
        subroutine_name = f"{self._symbol_attr.sub_class}.{name}"

        # Args
        n_args = 0
        while self._buffer:
            kind, _ = self._buffer.popleft()
            n_args += int(kind == "var")

        self._writer.write_call(subroutine_name, n_args)

    def _write_checked_token(self, tag: str,
                             content: Union[str, List[str]] = "",
                             dec: Union[str, List[str]] = ""
                             ) -> Tuple[str, str]:
        """Writes current token with syntax check.

        Args:
            tag (str): Expected tag.
            content (str or list[str], optional): Expected content.
            dec (str or list[str], optional): Identifier type.

        Returns:
            tag (str): Tag of the specified token.
            content (str): Content of the specified token.
        """

        cur_tag, cur_content = super()._write_checked_token(tag, content)

        def _check_dec(given: Union[str, List[str]], target: str) -> bool:
            if isinstance(given, str):
                given = [given]
            return any(v == target for v in given)

        if cur_tag == "keyword" and cur_content in self.kind_list:
            self._symbol_attr.kind = cur_content

        if cur_tag == "identifier" and _check_dec(dec, "class"):
            if self._is_defined:
                self._symbol_attr.class_name = cur_content
            self._symbol_attr.sub_class = cur_content

        if cur_tag == "identifier" and _check_dec(dec, "subroutine"):
            cur_content = f"{self._symbol_attr.sub_class}.{cur_content}"

        if cur_tag == "identifier" and _check_dec(dec, "var"):
            if self._is_defined and cur_content not in self._symbol_table:
                self._symbol_table.define(
                    cur_content, self._symbol_attr.type, self._symbol_attr.kind
                )

        # Write output token
        if cur_tag == "identifier":
            if _check_dec(dec, "var") and cur_content in self._symbol_table:
                # In method calling, the program can accept 'var.method()'
                # or 'class.method()'. We cannnot distinguish between these
                # two.
                element = self._symbol_table[cur_content]
                token = f"{dataclasses.asdict(element)}, "
            else:
                token = ""
            token = (f"<{cur_tag}> {dataclasses.asdict(self._symbol_attr)}, "
                     f"{token}{cur_content} </{cur_tag}>")
            self._code.pop()
            self._code.append(token)

        # Buffer
        if not self._is_defined:
            if _check_dec(dec, "subroutine"):
                self._buffer.append(("subroutine", cur_content))
            elif _check_dec(dec, "argument") or _check_dec(dec, "var"):
                self._buffer.append(("argument", cur_content))
            elif _check_dec(dec, "integerConstant"):
                self._buffer.append(("constant", cur_content))
            elif _check_dec(dec, "stringConstant"):
                self._buffer.append(("string", cur_content))
            else:
                raise NotImplementedError(f"{dec}, {cur_content}")

        if _check_dec(dec, "var"):
            self._buffer.append(("var", cur_content))

        return cur_tag, cur_content

    def _write_checked_type(self, allow_void: bool = False) -> Tuple[str, str]:
        """Writes current type with syntax check.

        type: ('int | 'char' | 'boolean', className)

        Args:
            allow_void (bool, optional): If `True`, 'void' type is allowed.

        Returns:
            tag (str): Tag of the specified token.
            content (str): Content of the specified token.
        """

        tag, content = super()._write_checked_type(allow_void)
        self._symbol_attr.type = content

        return tag, content

    def _write_checked_ops(self) -> Tuple[str, str]:
        """Writes current operator with syntax check.

        type: ("+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "=")

        Returns:
            tag (str): Tag of the specified token.
            content (str): Content of the specified token.
        """

        _tag, _op = super()._write_checked_ops()

        if _op in self.unary_ops_table:
            self._writer.write_arithmetic(self.unary_ops_table[_op])
        elif _op in self.ops_table:
            self._writer.write_arithmetic(self.ops_table[_op])
        elif _op == "*":
            self._writer.write_call("Math.multiply", 2)
        elif _op == "/":
            self._writer.write_call("Math.devide", 2)
        else:
            raise ValueError(f"Unexpected operand: {_op}")

        return _tag, _op
