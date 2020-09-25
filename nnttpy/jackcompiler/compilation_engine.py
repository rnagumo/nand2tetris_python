
from typing import List, Union, Tuple, Optional


class XMLCompilationEngine:
    """Compile engine."""

    class_var_dec_tokens = ["static", "field"]
    subroutine_tokens = ["constructor", "function", "method"]
    statement_tokens = ["let", "if", "while", "do", "return"]
    type_tokens = ["int", "char", "boolean"]
    ops = ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]
    unary_ops = ["-", "~"]
    keyword_constant = ["true", "false", "null", "this"]
    identifier_type = ["class", "subroutine", "var"]

    def __init__(self):

        self._token_list: List[str] = []
        self._line_list: List[int] = []
        self._index = 0
        self._code: List[str] = []

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
        self._code = []
        self.compile_class()

        return self._code[:]

    def compile_class(self) -> None:
        """Compiles class.

        'class' className '{' classVarDec* subroutineDec* '}'
        """

        self._write_non_terminal_tag("class")

        # 'class' className
        self._write_checked_token("keyword", "class")
        self._write_checked_token("identifier")

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

    def compile_class_var_dec(self) -> None:
        """Compiles classVarDec.

        ('static'|'field') type varName (',', varName)* ';'
        """

        # ('static'|'field') type varName
        self._write_non_terminal_tag("classVarDec")
        self._write_checked_token("keyword", self.class_var_dec_tokens)
        self._write_checked_type()
        self._write_checked_token("identifier")

        # (',', varName)*
        while self._check_syntax("symbol", ","):
            self._write_checked_token("symbol", ",")
            self._write_checked_token("identifier")

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

        # ('void'|type) subroutineName
        self._write_checked_type(allow_void=True)
        self._write_checked_token("identifier")

        # '(' parameterList ')' subroutineBody
        self._write_checked_token("symbol", "(")
        self.compile_parameter_list()
        self._write_checked_token("symbol", ")")
        self.compile_subroutine_body()
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
        self._write_checked_type()
        self._write_checked_token("identifier")
        num_params = 1

        # (',' type varName)*
        while self._check_syntax("symbol", ","):
            self._write_checked_token("symbol", ",")
            self._write_checked_type()
            self._write_checked_token("identifier")
            num_params += 1

        self._write_non_terminal_tag("/parameterList")

        return num_params

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
        self._write_checked_type()
        self._write_checked_token("identifier")

        # (',' varName)*
        while self._check_syntax("symbol", ","):
            self._write_checked_token("symbol", ",")
            self._write_checked_token("identifier")

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
            if self._check_syntax("keyword", "do"):
                self.compile_do()
            elif self._check_syntax("keyword", "let"):
                self.compile_let()
            elif self._check_syntax("keyword", "while"):
                self.compile_while()
            elif self._check_syntax("keyword", "return"):
                self.compile_return()
            elif self._check_syntax("keyword", "if"):
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

        # 'let' varName
        self._write_non_terminal_tag("letStatement")
        self._write_checked_token("keyword", "let")
        self._write_checked_token("identifier")

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
        while self._check_ops():
            self._write_checked_ops()
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
        elif self._check_syntax("keyword", self.keyword_constant):
            self._write_checked_token("keyword", self.keyword_constant)
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

        if self._check_next_syntax("symbol", "."):
            self._write_checked_token("identifier")
            self._write_checked_token("symbol", ".")
            self._write_checked_token("identifier")
        else:
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

    def _check_syntax(self, tag: str, content: Union[str, List[str]] = "",
                      raises: bool = False, index: Optional[int] = None
                      ) -> bool:
        """Checks syntax of current token.

        Args:
            tag (str): Expected tag.
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

        index = index if index is not None else self._index
        cur_tag, cur_content = self._get_contents(index)

        flag = cur_tag == tag
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

    def _check_next_syntax(self, tag: str, content: Union[str, List[str]] = ""
                           ) -> bool:
        """Checks next syntax.

        This method is used for compiling `term` element.

        Args:
            tag (str): Expected tag.
            content (str or list[str], optional): Expected content.
        """

        return self._check_syntax(tag, content, index=self._index + 1)

    def _check_type(self, allow_void: bool = False, raises: bool = False,
                    index: Optional[int] = None) -> bool:
        """Checks type validation of current token.

        Args:
            allow_void (bool, optional): If `True`, 'void' type is allowed.
            raises (bool, optional): Whether raises error.
            index (int, optional): Index you focus on.

        Returns:
            checked (bool): If `True`, current token is expected one.
        """

        index = index if index is not None else self._index
        cur_tag, cur_content = self._get_contents(index)

        flag = False
        flag |= self._check_syntax(
                "keyword", self.type_tokens, raises=False, index=index)
        flag |= self._check_syntax("identifier", raises=False, index=index)
        if allow_void:
            flag |= self._check_syntax(
                "keyword", "void", raises=False, index=index)

        if not flag and raises:
            raise SyntaxError(
                f"Expected valid type, but given tag='{cur_tag}' and "
                f"content='{cur_content}' at line {self._line_list[index]}.")

        return flag

    def _check_ops(self, raises: bool = False) -> bool:
        """Checks operator of current token.

        Args:
            raises (bool, optional): Whether raises error.

        Returns:
            checked (bool): If `True`, current token is expected one.
        """

        cur_tag, cur_content = self._get_contents(self._index)
        flag = self._check_syntax("symbol", self.ops, raises=False)

        if not flag and raises:
            raise SyntaxError(
                f"Expected valid type, but given tag='{cur_tag}' and "
                f"content='{cur_content}' at line "
                "{self._line_list[self._index]}.")

        return flag

    def _write_checked_token(self, tag: str,
                             content: Union[str, List[str]] = "") -> str:
        """Writes current token with syntax check.

        Args:
            tag (str): Expected tag.
            content (str or list[str], optional): Expected content.

        Returns:
            content (str): Content of the specified token.
        """

        self._check_syntax(tag, content, raises=True)
        self._code.append(self._token_list[self._index])
        self._index += 1

        _, _content = self._get_contents(self._index - 1)
        return _content

    def _write_checked_type(self, allow_void: bool = False) -> str:
        """Writes current type with syntax check.

        type: ('int | 'char' | 'boolean', className)

        Args:
            allow_void (bool, optional): If `True`, 'void' type is allowed.

        Returns:
            tag (str): Tag of the specified token.
        """

        self._check_type(allow_void, raises=True)
        self._code.append(self._token_list[self._index])
        self._index += 1

        _, _content = self._get_contents(self._index - 1)
        return _content

    def _write_checked_ops(self) -> str:
        """Writes current operator with syntax check.

        type: ("+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "=")

        Returns:
            tag (str): Tag of the specified token.
        """

        self._check_ops(raises=True)
        self._code.append(self._token_list[self._index])
        self._index += 1

        _, _content = self._get_contents(self._index - 1)
        return _content

    def _write_non_terminal_tag(self, tag: str) -> None:
        """Writes non terminal tag.

        Args:
            tag (str): Tag name without bracket "<>".
        """

        self._code.append(f"<{tag}>")

    def _get_contents(self, index: int) -> Tuple[str, str]:
        """Gets tag & content of given index.

        Args:
            index (int): Index value.

        Returns:
            tag (str): Tag of the specified token.
            content (str): Content of the specified token.
        """

        _tag, *_content, _ = self._token_list[index].split(" ")
        tag = _tag.strip("<>")
        content = " ".join(_content)

        return tag, content
