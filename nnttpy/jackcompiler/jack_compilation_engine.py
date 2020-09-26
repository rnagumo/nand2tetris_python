
from typing import List, Tuple

from nnttpy import jackcompiler


class JackCompileEngine(jackcompiler.XMLCompilationEngine):
    """Symbol engine with symbol table."""

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
        self._writer = jackcompiler.VMWriter()
        self._class_name = ""

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
        self._write_non_terminal_tag("class")

        # 'class' className
        self._write_checked_token("keyword", "class")
        self._class_name = self._write_checked_token("identifier")

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

    def compile_class_var_dec(self):
        """Compiles classVarDec.

        ('static'|'field') type varName (',', varName)* ';'
        """

        # ('static'|'field') type varName
        self._write_non_terminal_tag("classVarDec")
        var_kind = self._write_checked_token(
            "keyword", self.class_var_dec_tokens)
        var_type = self._write_checked_type()
        var_name = self._write_checked_token("identifier")
        self._symbol_table.define(var_name, var_type, var_kind)

        # (',', varName)*
        while self._check_syntax("symbol", ","):
            self._write_checked_token("symbol", ",")
            self._write_checked_token("identifier")
            var_name = self._write_checked_token("identifier")
            self._symbol_table.define(var_name, var_type, var_kind)

        self._write_checked_token("symbol", ";")
        self._write_non_terminal_tag("/classVarDec")

    def compile_subroutine(self) -> None:
        """Compiles subroutine.

        ('constructor'|'function'|'method') ('void'|type) subroutineName
        '(' parameterList ')' subroutineBody
        """

        self._symbol_table.start_subroutine()
        self._write_non_terminal_tag("subroutineDec")

        # ('constructor'|'function'|'method')
        self._write_checked_token("keyword", self.subroutine_tokens)

        # ('void'|type) subroutineName
        self._write_checked_type(allow_void=True)
        subroutine_name = self._write_checked_token("identifier")

        # '(' parameterList ')' subroutineBody
        self._write_checked_token("symbol", "(")
        self.compile_parameter_list()
        self._write_checked_token("symbol", ")")

        # subroutineBody
        self.compile_subroutine_body(subroutine_name)
        self._write_non_terminal_tag("/subroutineDec")

    def compile_parameter_list(self) -> int:
        """Compiles parameter list.

        ((type varName) (',' type varName)*)?

        Returns:
            num_params (int): Numnber of parameters.
        """

        self._write_non_terminal_tag("parameterList")
        if not self._check_type():
            self._write_non_terminal_tag("/parameterList")
            return 0

        # type varName
        var_type = self._write_checked_type()
        var_name = self._write_checked_token("identifier")
        self._symbol_table.define(var_name, var_type, "argument")
        num_params = 1

        # (',' type varName)*
        while self._check_syntax("symbol", ","):
            self._write_checked_token("symbol", ",")
            var_type = self._write_checked_type()
            var_name = self._write_checked_token("identifier")
            self._symbol_table.define(var_name, var_type, "argument")
            num_params += 1

        self._write_non_terminal_tag("/parameterList")

        return num_params

    def compile_subroutine_body(self, subroutine_name: str) -> None:
        """Compiles subroutine body.

        '{' varDec* statements '}'

        Args:
            subroutine_name (str): Subroutine name.
        """

        self._write_non_terminal_tag("subroutineBody")
        self._write_checked_token("symbol", "{")

        # varDec*
        num_locals = 0
        while self._check_syntax("keyword", "var"):
            num_locals += self.compile_var_dec()
        self._writer.write_function(subroutine_name, num_locals)

        # statements '}'
        self.compile_statements()
        self._write_checked_token("symbol", '}')
        self._write_non_terminal_tag("/subroutineBody")

    def compile_var_dec(self) -> int:
        """Compiles variable declaration.

        'var' type varName (',' varName)* ';'

        Returns:
            num_vars (int): Number of variables.
        """

        num_vars = 0

        # 'var' type varName
        self._write_non_terminal_tag("varDec")
        self._write_checked_token("keyword", "var")
        var_type = self._write_checked_type()
        var_name = self._write_checked_token("identifier")
        self._symbol_table.define(var_name, var_type, "argument")
        num_vars += 1

        # (',' varName)*
        while self._check_syntax("symbol", ","):
            self._write_checked_token("symbol", ",")
            var_name = self._write_checked_token("identifier")
            self._symbol_table.define(var_name, var_type, "argument")
            num_vars += 1

        self._write_checked_token("symbol", ";")
        self._write_non_terminal_tag("/varDec")

        return num_vars

    def compile_let(self) -> None:
        """Compiles let statement.

        'let' varName ('[' expression ']')? '=' expression ';'
        """

        # 'let' varName
        self._write_non_terminal_tag("letStatement")
        self._write_checked_token("keyword", "let")
        var_name = self._write_checked_token("identifier")
        symbol = self._symbol_table[var_name]

        # ('[' expression ']')?
        if self._check_syntax("symbol", "["):
            do_array_assign = True
            self._write_checked_token("symbol", "[")
            self.compile_expression()
            self._write_checked_token("symbol", "]")

            self._writer.write_push(symbol.kind, symbol.number)
            self._writer.write_arithmetic("add")
        else:
            do_array_assign = False

        # '=' expression ';'
        self._write_checked_token("symbol", "=")
        self.compile_expression()
        self._write_checked_token("symbol", ";")
        self._write_non_terminal_tag("/letStatement")

        if do_array_assign:
            # Pop returned value to temp
            self._writer.write_pop("temp", 0)

            # Pop address of array slot to THAT
            self._writer.write_pop("pointer", 1)

            # Push popped returned value to temp
            self._writer.write_push("temp", 0)

            # Set popped address to THAT
            self._writer.write_pop("that", 0)
        else:
            self._writer.write_pop(symbol.kind, symbol.number)

    def compile_expression(self) -> None:
        """Compiles expression.

        term (op term)*
        """

        ops_list: List[Tuple[str, str]] = []

        self._write_non_terminal_tag("expression")
        self.compile_term(ops_list)
        while self._check_ops():
            _op = self._write_checked_ops()
            ops_list.append((_op, "bi"))
            self.compile_term(ops_list)
        self._write_non_terminal_tag("/expression")

        while ops_list:
            _op, _category = ops_list.pop()
            if _category == "unary":
                self._writer.write_arithmetic(self.unary_ops_table[_op])
            elif _op == "*":
                self._writer.write_call("Math.multiply", 2)
            elif _op == "/":
                self._writer.write_call("Math.devide", 2)
            else:
                self._writer.write_arithmetic(self.ops_table[_op])

    def compile_term(self, ops_list: list) -> None:
        """Compiles term.

        integerConstant | stringConstant | keywordConstant |
        '(' expression ')' | unaryOp term |
        varName | varName '[' expression ']' | subroutineCall

        Args:
            ops_list (list): List of operations
        """

        self._write_non_terminal_tag("term")
        if self._check_syntax("integerConstant"):
            _constant = self._write_checked_token("integerConstant")
            self._writer.write_push("constant", _constant)
        elif self._check_syntax("stringConstant"):
            self._write_checked_token("stringConstant")
        elif self._check_syntax("keyword", self.keyword_constant):
            self._write_checked_token("keyword", self.keyword_constant)
        elif self._check_syntax("symbol", "("):
            self._write_checked_token("symbol", "(")
            self.compile_expression()
            self._write_checked_token("symbol", ")")
        elif self._check_syntax("symbol", self.unary_ops):
            _op = self._write_checked_token("symbol", self.unary_ops)
            ops_list.append((_op, "unary"))
            self.compile_term(ops_list)
        elif self._check_syntax("identifier"):
            if self._check_next_syntax("symbol", "["):
                self._write_checked_token("identifier")
                self._write_checked_token("symbol", "[")
                self.compile_expression()
                self._write_checked_token("symbol", "]")
            elif self._check_next_syntax("symbol", [".", "("]):
                self.compile_subroutine_call()
            else:
                self._write_checked_token("identifier")

        self._write_non_terminal_tag("/term")

    def compile_subroutine_call(self) -> None:
        """Compiles subroutine call.

        subroutineName '(' expressionList ')' |
        (className|varName) '.' subroutineName '(' expressionList ')'
        """

        if self._check_next_syntax("symbol", "."):
            # User defined method
            caller_name = self._write_checked_token("identifier")
            self._write_checked_token("symbol", ".")
            subroutine_name = self._write_checked_token("identifier")
        else:
            caller_name = ""
            subroutine_name = self._write_checked_token("identifier")

        if caller_name in self._symbol_table:
            method_call = True
            symbol = self._symbol_table[caller_name]
            symbol_type = symbol.type
            self._writer.write_push("local", symbol.number)
        else:
            method_call = False
            symbol_type = caller_name
        subroutine_call_name = f"{symbol_type}.{subroutine_name}"

        self._write_checked_token("symbol", "(")
        num_args = self.compile_expression_list(
            is_empty=self._check_syntax("symbol", ")"))
        self._write_checked_token("symbol", ")")

        if method_call:
            num_args += 1

        self._writer.write_call(subroutine_call_name, num_args)
        self._writer.write_pop("temp", 0)

    def compile_expression_list(self, is_empty: bool = False) -> int:
        """Compiles expression list.

        (expression (',' expression)* )?

        Args:
            is_empty (bool, optional): If this expression list is empty.

        Returns:
            num_args (int): Number of arguments
        """

        self._write_non_terminal_tag("expressionList")

        num_args = 0
        if not is_empty:
            self.compile_expression()
            while self._check_syntax("symbol", ","):
                self._write_checked_token("symbol", ",")
                self.compile_expression()
                num_args += 1

        self._write_non_terminal_tag("/expressionList")

        return num_args
