
from typing import List, Union

import dataclasses

from nnttpy import jackcompiler


@dataclasses.dataclass
class SymbolAttr:
    class_name: str = ""
    category: str = ""
    type: str = ""
    kind: str = ""


class JackCompileEngine(jackcompiler.XMLCompilationEngine):
    """Symbol engine with symbol table."""

    category_list = [
        "static", "field", "arg", "var", "class", "subroutine"]
    kind_list = ["static", "field", "arg", "var"]

    def __init__(self):
        super().__init__()

        self._symbol_table = jackcompiler.SymbolTable()
        self._symbol_attr = SymbolAttr()
        self._is_defined = False

    def compile_class(self) -> None:
        """Compiles class.

        'class' className '{' classVarDec* subroutineDec* '}'
        """

        self._symbol_table.start_class()
        self._symbol_attr.category = "class"
        self._is_defined = False

        self._write_non_terminal_tag("class")

        # 'class' className
        self._write_checked_token("keyword", "class")
        class_name = self._write_checked_token("identifier")
        self._symbol_attr.class_name = class_name
        self._type_names.append(class_name)
        self._class_names.append(class_name)

        # '{' classVarDec* subroutineDec*
        self._write_checked_token("symbol", "{")
        while not self._check_syntax("symbol", "}"):
            if self._check_syntax("keyword", self.class_var_dec_tokens):
                self.compile_class_var_dec()
            elif self._check_syntax("keyword", self.subroutine_tokens):
                self.compile_subroutine()
            else:
                self._check_syntax(
                    "keyword",
                    self.class_var_dec_tokens + self.subroutine_tokens,
                    raises=True)

        self._write_checked_token("symbol", "}")
        self._write_non_terminal_tag("/class")

        # Finally, abord parameters
        self._static_var_names = []
        self._field_var_names = []

    def compile_class_var_dec(self) -> None:
        """Compiles classVarDec.

        ('static'|'field') type varName (',', varName)* ';'
        """

        self._is_defined = True
        self._write_non_terminal_tag("classVarDec")

        # ('static'|'field')
        scope = self._write_checked_token("keyword", self.class_var_dec_tokens)
        self._symbol_attr.category = scope
        self._symbol_attr.kind = scope

        # type
        var_type = self._write_checked_token(["keyword", "identifier"])
        self._symbol_attr.type = var_type

        # varName
        var_name = self._write_checked_identifier("identifier")
        if scope == "static":
            self._static_var_names.append(var_name)
        else:
            self._field_var_names.append(var_name)

        # (',', varName)*
        while self._check_syntax("symbol", ","):
            self._write_checked_token("symbol", ",")
            var_name = self._write_checked_identifier("identifier")
            if scope == "static":
                self._static_var_names.append(var_name)
            else:
                self._field_var_names.append(var_name)

        self._write_checked_token("symbol", ";")
        self._write_non_terminal_tag("/classVarDec")
        self._is_defined = False

    def compile_subroutine(self) -> None:
        """Compiles subroutine.

        ('constructor'|'function'|'method') ('void'|type) subroutineName
        '(' parameterList ')' subroutineBody
        """

        self._symbol_table.start_subroutine()
        return super().compile_subroutine()

    def compile_parameter_list(self) -> None:
        """Compiles parameter list.

        ((type varName) (',' type varName)*)?
        """

        self._is_defined = True
        self._symbol_attr.category = "arg"
        self._symbol_attr.kind = "arg"

        self._write_non_terminal_tag("parameterList")
        if not self._check_syntax(content=self._type_names):
            self._write_non_terminal_tag("/parameterList")
            return

        # type
        var_type = self._write_checked_token(content=self._type_names)
        self._symbol_attr.type = var_type

        # varName
        var_name = self._write_checked_identifier("identifier")
        self._param_var_names.append(var_name)

        # (',' type varName)*
        while self._check_syntax("symbol", ","):
            self._write_checked_token("symbol", ",")
            var_type = self._write_checked_token(content=self._type_names)
            self._symbol_attr.type = var_type
            var_name = self._write_checked_identifier("identifier")
            self._param_var_names.append(var_name)

        self._write_non_terminal_tag("/parameterList")
        self._is_defined = False

    def compile_var_dec(self) -> None:
        """Compiles variable declaration.

        'var' type varName (',' varName)* ';'
        """

        self._is_defined = True
        self._symbol_attr.category = "var"
        self._symbol_attr.kind = "var"

        # 'var' type varName
        self._write_non_terminal_tag("varDec")
        self._write_checked_token("keyword", "var")
        var_type = self._write_checked_token(["keyword", "identifier"])
        self._symbol_attr.type = var_type
        var_name = self._write_checked_token("identifier")
        self._local_var_names.append(var_name)

        # (',' varName)*
        while self._check_syntax("symbol", ","):
            self._write_checked_token("symbol", ",")
            var_name = self._write_checked_token("identifier")
            self._local_var_names.append(var_name)

        self._write_checked_token("symbol", ";")
        self._write_non_terminal_tag("/varDec")
        self._is_defined = False

    def _write_checked_identifier(self, tag: Union[str, List[str]] = "",
                                  content: Union[str, List[str]] = "") -> str:
        """Writes current identifier with syntax check.

        Args:
            tag (str or list[str], optional): Expected tag.
            content (str or list[str], optional): Expected content.

        Returns:
            content (str): Current content.

        Raises:
            SyntaxError: If given identifier does not exist in symbol table.
        """

        self._check_syntax(tag, content, raises=True)

        _cur_tag, *_cur_content, _ = self._token_list[self._index].split(" ")
        cur_tag = _cur_tag.strip("<>")
        cur_content = " ".join(_cur_content)

        if self._is_defined and (cur_content not in self._symbol_table):
            self._symbol_table.define(
                cur_content, self._symbol_attr.type, self._symbol_attr.kind)

        try:
            element = self._symbol_table[cur_content]
        except KeyError as e:
            raise SyntaxError(
                f"Undefined variable '{cur_content}' is found ad line at "
                f"{self._line_list[self._index]}") from e

        token = (
            f"<{cur_tag}> {self._symbol_attr.category}, {self._is_defined}, "
            f"{element.kind}, {element.number}, {cur_content} </{cur_tag}>")

        self._code.append(token)
        self._index += 1

        return cur_content
