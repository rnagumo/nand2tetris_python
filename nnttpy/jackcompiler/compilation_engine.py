
from typing import List, Union, Tuple, Optional


class XMLCompilationEngine:
    """Compile engine."""

    type_tokens = ["boolean", "int", "char"]
    class_var_dec_tokens = ["static", "field"]
    subroutine_tokens = ["constructor", "function", "method"]
    statement_tokens = ["let", "if", "while", "do", "return"]
    ops = ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]
    unary_ops = ["-", "~"]
    keyword_constant = ["true", "false", "null", "this"]

    def __init__(self):

        self._token_list: List[str] = []
        self._line_list: List[int] = []
        self._index = 0
        self._code: List[str] = []

        # Used-defined type/class/subroutine names
        self._type_names: List[str] = self.type_tokens[:]
        self._class_names: List[str] = []
        self._subroutine_names: List[str] = []

        # Variable names
        self._static_var_names: List[str] = []  # class
        self._field_var_names: List[str] = []  # object
        self._local_var_names: List[str] = []  # subroutine
        self._param_var_names: List[str] = []  # subroutine

    @property
    def code(self) -> List[str]:
        return self._code

    @property
    def var_names(self) -> List[str]:
        return (self._static_var_names + self._field_var_names
                + self._local_var_names + self._param_var_names)

    def compile(self, token_list: List[Tuple[int, str]]) -> List[str]:
        """Compiles given token list.

        Caution: This method should be called first.

        Args:
            token_list (list of [int, str]): List of line number and tokens
                ('<tag> content </tag>').

        Returns:
            code_list (list of str): Compiled codes.
        """

        self._token_list = [t for _, t in token_list]
        self._line_list = [n for n, _ in token_list]
        self._index = 0
        self.compile_class()

        return self._code[:]

    def compile_class(self) -> None:
        """Compiles class.

        'class' className '{' classVarDec* subroutineDec* '}'
        """

        self._write_non_terminal_tag("class")

        # 'class' className
        self._write_checked_token("keyword", "class")
        class_name = self._write_checked_token("identifier")
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

        self._write_non_terminal_tag("classVarDec")

        # ('static'|'field')
        scope = self._write_checked_token("keyword", self.class_var_dec_tokens)

        # type
        self._write_checked_token(["keyword", "identifier"])

        # varName
        var_name = self._write_checked_token("identifier")
        if scope == "static":
            self._static_var_names.append(var_name)
        else:
            self._field_var_names.append(var_name)

        # (',', varName)*
        while self._check_syntax("symbol", ","):
            self._write_checked_token("symbol", ",")
            var_name = self._write_checked_token("identifier")
            if scope == "static":
                self._static_var_names.append(var_name)
            else:
                self._field_var_names.append(var_name)

        self._write_checked_token("symbol", ";")
        self._write_non_terminal_tag("/classVarDec")

    def compile_subroutine(self) -> None:
        """Compiles subroutine.

        ('constructor'|'function'|'method') ('void'|type) subroutineName
        '(' parameterList ')' subroutineBody
        """

        self._write_non_terminal_tag("subroutineDec")

        # ('constructor'|'function'|'method')
        self._write_checked_token("keyword", self.subroutine_tokens)

        # ('void'|type)
        self._write_checked_token(content=self._type_names + ["void"])

        # subroutineName
        subroutine_name = self._write_checked_token("identifier")
        self._subroutine_names.append(subroutine_name)

        # '(' parameterList ')' subroutineBody
        self._write_checked_token("symbol", "(")
        self.compile_parameter_list()
        self._write_checked_token("symbol", ")")
        self.compile_subroutine_body()
        self._write_non_terminal_tag("/subroutineDec")

        # Finally, abord local/parameter list
        self._local_var_names = []
        self._param_var_names = []

    def compile_parameter_list(self) -> None:
        """Compiles parameter list.

        ((type varName) (',' type varName)*)?
        """

        self._write_non_terminal_tag("parameterList")
        if not self._check_syntax(content=self._type_names):
            self._write_non_terminal_tag("/parameterList")
            return

        # type varName
        self._write_checked_token(content=self._type_names)
        var_name = self._write_checked_token("identifier")
        self._param_var_names.append(var_name)

        # (',' type varName)*
        while self._check_syntax("symbol", ","):
            self._write_checked_token("symbol", ",")
            self._write_checked_token(content=self._type_names)
            var_name = self._write_checked_token("identifier")
            self._param_var_names.append(var_name)

        self._write_non_terminal_tag("/parameterList")

    def compile_subroutine_body(self) -> None:
        """Compiles subroutine body.

        '{' varDec* statements '}'
        """

        self._write_non_terminal_tag("subroutineBody")
        self._write_checked_token("symbol", "{")

        # varDec*
        while self._check_syntax("keyword", "var"):
            self.compile_var_dec()

        # statements '}'
        self.compile_statements()
        self._write_checked_token("symbol", '}')
        self._write_non_terminal_tag("/subroutineBody")

    def compile_var_dec(self) -> None:
        """Compiles variable declaration.

        'var' type varName (',' varName)* ';'
        """

        # 'var' type varName
        self._write_non_terminal_tag("varDec")
        self._write_checked_token("keyword", "var")
        self._write_checked_token(["keyword", "identifier"])
        var_name = self._write_checked_token("identifier")
        self._local_var_names.append(var_name)

        # (',' varName)*
        while self._check_syntax("symbol", ","):
            self._write_checked_token("symbol", ",")
            var_name = self._write_checked_token("identifier")
            self._local_var_names.append(var_name)

        self._write_checked_token("symbol", ";")
        self._write_non_terminal_tag("/varDec")

    def compile_statements(self) -> None:
        """Compiles statements.

        statements: statement*
        statement:
            letStatement|ifStatement|whileStatement|doStatement|returnStatement
        """

        self._write_non_terminal_tag("statements")

        # statement*
        while self._check_syntax("keyword", self.statement_tokens):
            if self._check_syntax(content="do"):
                self.compile_do()
            elif self._check_syntax(content="let"):
                self.compile_let()
            elif self._check_syntax(content="while"):
                self.compile_while()
            elif self._check_syntax(content="return"):
                self.compile_return()
            elif self._check_syntax(content="if"):
                self.compile_if()

        self._write_non_terminal_tag("/statements")

    def compile_do(self) -> None:
        """Compiles do statement.

        'do' subroutineCall ';'
        """

        self._write_non_terminal_tag("doStatement")
        self._write_checked_token("keyword", "do")
        self.compile_subroutine_call()
        self._write_checked_token("symbol", ";")
        self._write_non_terminal_tag("/doStatement")

    def compile_let(self) -> None:
        """Compiles let statement.

        'let' varName ('[' expression ']')? '=' expression ';'
        """

        self._write_non_terminal_tag("letStatement")
        self._write_checked_token("keyword", "let")

        # varName
        self._write_checked_token(
            "identifier",
            content=(self._static_var_names + self._field_var_names
                     + self._local_var_names + self._param_var_names)
        )

        # ('[' expression ']')?
        if self._check_syntax("symbol", "["):
            self._write_checked_token("symbol", "[")
            self.compile_expression()
            self._write_checked_token("symbol", "]")

        # '=' expression ';'
        self._write_checked_token("symbol", "=")
        self.compile_expression()
        self._write_checked_token("symbol", ";")
        self._write_non_terminal_tag("/letStatement")

    def compile_while(self) -> None:
        """Compiles while statement.

        'while' '(' expression ')' '{' statements '}'
        """

        self._write_non_terminal_tag("whileStatement")
        self._write_checked_token("keyword", "while")
        self._write_checked_token("symbol", "(")
        self.compile_expression()
        self._write_checked_token("symbol", ")")
        self._write_checked_token("symbol", "{")
        self.compile_statements()
        self._write_checked_token("symbol", "}")
        self._write_non_terminal_tag("/whileStatement")

    def compile_return(self) -> None:
        """Compiles return statement.

        'return' expression? ';'
        """

        self._write_non_terminal_tag("returnStatement")
        self._write_checked_token("keyword", "return")
        if not self._check_syntax("symbol", ";"):
            self.compile_expression()
        self._write_checked_token("symbol", ";")
        self._write_non_terminal_tag("/returnStatement")

    def compile_if(self) -> None:
        """Compiles if statement.

        'if' '(' expression ')' '{' statements '}'
        ('else' '{' statements '}')?
        """

        self._write_non_terminal_tag("ifStatement")
        self._write_checked_token("keyword", "if")
        self._write_checked_token("symbol", "(")
        self.compile_expression()
        self._write_checked_token("symbol", ")")
        self._write_checked_token("symbol", "{")
        self.compile_statements()
        self._write_checked_token("symbol", "}")

        if self._check_syntax("keyword", "else"):
            self._write_checked_token("keyword", "else")
            self._write_checked_token("symbol", "{")
            self.compile_statements()
            self._write_checked_token("symbol", "}")

        self._write_non_terminal_tag("/ifStatement")

    def compile_expression(self) -> None:
        """Compiles expression.

        term (op term)*
        """

        self._write_non_terminal_tag("expression")
        self.compile_term()
        while self._check_syntax("symbol", self.ops):
            self._write_checked_token("symbol", self.ops)
            self.compile_term()
        self._write_non_terminal_tag("/expression")

    def compile_term(self) -> None:
        """Compiles term.

        integerConstant | stringConstant | keywordConstant |
        '(' expression ')' | unaryOp term |
        varName | varName '[' expression ']' | subroutineCall
        """

        self._write_non_terminal_tag("term")
        if self._check_syntax("integerConstant"):
            self._write_checked_token("integerConstant")
        elif self._check_syntax("stringConstant"):
            self._write_checked_token("stringConstant")
        elif self._check_syntax(content=self.keyword_constant):
            self._write_checked_token(content=self.keyword_constant)
        elif self._check_syntax("symbol", "("):
            self._write_checked_token("symbol", "(")
            self.compile_expression()
            self._write_checked_token("symbol", ")")
        elif self._check_syntax("symbol", self.unary_ops):
            self._write_checked_token("symbol", self.unary_ops)
            self.compile_term()
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

        self._write_checked_token("identifier")
        if self._check_syntax("symbol", "."):
            self._write_checked_token("symbol", ".")
            self._write_checked_token("identifier")
        self._write_checked_token("symbol", "(")
        self.compile_expression_list(
            is_empty=self._check_syntax("symbol", ")"))
        self._write_checked_token("symbol", ")")

    def compile_expression_list(self, is_empty: bool = False) -> None:
        """Compiles expression list.

        (expression (',' expression)* )?

        Args:
            is_empty (bool, optional): If this expression list is empty.
        """

        self._write_non_terminal_tag("expressionList")
        if not is_empty:
            self.compile_expression()
            while self._check_syntax("symbol", ","):
                self._write_checked_token("symbol", ",")
                self.compile_expression()

        self._write_non_terminal_tag("/expressionList")

    def _check_syntax(self, tag: Union[str, List[str]] = "",
                      content: Union[str, List[str]] = "",
                      raises: bool = False,
                      index: Optional[int] = None) -> bool:
        """Checks syntax of current token.

        Args:
            tag (str or list[str], optional): Expected tag.
            content (str or list[str], optional): Expected content.
            raises (bool, optional): Whether raises error.
            index (int, optional): Index you focus on.

        Returns:
            checked (bool): If `True`, current token is expected one.

        Raises:
            ValueError: If `tag` and `content` are empty string.
            SyntaxError: If `raises` is `True` and `tag` or `content` do not
                match the current tag or content respectively.
        """

        if not tag and not content:
            raise ValueError("Both tag and content are empty.")

        if index is None:
            index = self._index

        _cur_tag, *_cur_content, _ = self._token_list[index].split(" ")
        cur_tag = _cur_tag.strip("<>")
        cur_content = " ".join(_cur_content)

        flag = True
        if tag:
            if isinstance(tag, str):
                tag = [tag]
            flag &= any(cur_tag == t for t in tag)
        if content:
            if isinstance(content, str):
                content = [content]
            flag &= any(cur_content == c for c in content)

        if not flag and raises:
            raise SyntaxError(
                f"Expected tag='{tag}' and content='{content}', but given "
                f"tag='{cur_tag}' and content='{cur_content}' at "
                f"line {self._line_list[index]}.")

        return flag

    def _check_next_syntax(self, tag: Union[str, List[str]] = "",
                           content: Union[str, List[str]] = "") -> bool:
        """Checks next syntax.

        This method is used for compiling `term` element.

        Args:
            tag (str or list[str], optional): Expected tag.
            content (str or list[str], optional): Expected content.
        """

        return self._check_syntax(tag, content, index=self._index + 1)

    def _write_checked_token(self, tag: Union[str, List[str]] = "",
                             content: Union[str, List[str]] = "") -> str:
        """Writes current token with syntax check.

        Args:
            tag (str or list[str], optional): Expected tag.
            content (str or list[str], optional): Expected content.

        Returns:
            content (str): Current content.
        """

        self._check_syntax(tag, content, raises=True)

        _, *_cur_content, _ = self._token_list[self._index].split(" ")
        cur_content = " ".join(_cur_content)

        self._code.append(self._token_list[self._index])
        self._index += 1

        return cur_content

    def _write_non_terminal_tag(self, tag: str) -> None:
        """Writes non terminal tag.

        Args:
            tag (str): Tag name without bracket "<>".
        """

        self._code.append(f"<{tag}>")
