
from typing import List, Union, Tuple

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

    def __init__(self):
        super().__init__()

        self._symbol_table = jackcompiler.SymbolTable()
        self._symbol_attr = SymbolAttr()
        self._writer = jackcompiler.VMWriter()
        self._is_defined = False

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

        return self._writer.code

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
        super().compile_subroutine()
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
