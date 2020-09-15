
from typing import List, Union


class CompilationEngine:
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

    def compile(self, token_list: List[str]) -> List[str]:
        """Compiles given token list.

        Caution: This method should be called first.

        Args:
            token_list (list of str): List of tokens ('<tag> content </tag>').

        Returns:
            token_list (list of str): Parsed token list.
        """

        self._token_list = token_list
        self._index = 0
        self.compile_class()

        return self._token_list[:]

    def compile_class(self) -> None:
        """Compiles class.

        'class' className '{' classVarDec* subroutineDec* '}'
        """

        self._code.append("<class>")

        # 'class' className
        self._write_checked_token("keyword", "class")
        class_name = self._write_checked_token("identifier")
        self._type_names.append(class_name)
        self._class_names.append(class_name)

        # '{' classVarDec* subroutineDec*
        self._write_checked_token("symbol", "{")
        while not self._check_syntax("symbol", "}"):
            if self._check_syntax("keyword", self.class_var_dec_tokens):
                self.compile_class_var_doc()
            elif self._check_syntax("keyword", self.subroutine_tokens):
                self.compile_subroutine()
            else:
                self._check_syntax(
                    "keyword",
                    self.class_var_dec_tokens + self.subroutine_tokens,
                    raises=True)

        self._write_checked_token("symbol", "}")
        self._code.append("</class>")

        # Finally, abord parameters
        self._static_var_names = []
        self._field_var_names = []

    def compile_class_var_doc(self) -> None:
        """Compiles classVarDec.

        ('static'|'field') type varName (',', varName)* ';'
        """

        self._code.append("<subroutineDec>")

        # ('static'|'field')
        scope = self._write_checked_token("keyword", self.class_var_dec_tokens)

        # type
        self._write_checked_token(content=self._type_names)

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
        self._code.append("</subroutineDec>")

    def compile_subroutine(self) -> None:
        """Compiles subroutine.

        ('constructor'|'function'|'method') ('void'|type) subroutineName
        '(' parameterList ')' subroutineBody
        """

        self._code.append("<subroutineDec>")

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

        # Finally, abord local/parameter list
        self._local_var_names = []
        self._param_var_names = []

    def compile_parameter_list(self) -> None:
        """Compiles parameter list.

        ((type varName) (',' type varName)*)?
        """

        if not self._check_syntax(content=self._type_names):
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

    def compile_subroutine_body(self) -> None:
        """Compiles subroutine body.

        '{' varDec* statements '}'
        """

        self._write_checked_token("symbol", "{")

        # varDec*
        while self._check_syntax("keyword", "var"):
            self.compile_var_dec()

        # statements '}'
        self.compile_statements()
        self._write_checked_token("symbol", '}')

    def compile_var_dec(self) -> None:
        """Compiles variable declaration.

        'var' type varName (',' varName)* ';'
        """

        # 'var' type varName
        self._write_checked_token("keyword", "var")
        self._write_checked_token(content=self._type_names)
        var_name = self._write_checked_token("identifier")
        self._local_var_names.append(var_name)

        # (',' varName)*
        while self._check_syntax("symbol", ","):
            self._write_checked_token("symbol", ",")
            var_name = self._write_checked_token("identifier")
            self._local_var_names.append(var_name)

        self._write_checked_token("symbol", ";")

    def compile_statements(self) -> None:
        """Compiles statements.

        statements: statement*
        statement:
            letStatement|ifStatement|whileStatement|doStatement|returnStatement
        """

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

    def compile_do(self) -> None:
        """Compiles do statement.

        'do' subroutineCall ';'
        """

        self._write_checked_token("keyword", "do")
        self.compile_subroutine_call()
        self._write_checked_token("symbol", ";")

    def compile_let(self) -> None:
        """Compiles let statement.

        'let' varName ('[' expression ']')? '=' expression ';'
        """

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

    def compile_while(self) -> None:
        """Compiles while statement.

        'while' '(' expression ')' '{' statements '}'
        """

        self._write_checked_token("keyword", "while")
        self._write_checked_token("symbol", "(")
        self.compile_expression()
        self._write_checked_token("symbol", ")")
        self._write_checked_token("symbol", "{")
        self.compile_statements()
        self._write_checked_token("symbol", "}")

    def compile_return(self) -> None:
        """Compiles return statement.

        'return' expression? ';'
        """

        self._write_checked_token("keyword", "return")
        while not self._check_syntax("symbol", ";"):
            self.compile_expression()
        self._write_checked_token("symbol", ";")

    def compile_if(self) -> None:
        """Compiles if statement.

        'if' '(' expression ')' '{' statements '}'
        ('else' '{' statements '}')?
        """

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

    def compile_expression(self) -> None:
        """Compiles expression.

        term (op term)*
        """

        self.compile_term()
        while self._check_syntax("symbol", self.ops):
            self._write_checked_token("symbol", self.ops)
            self.compile_term()

    def compile_term(self) -> None:
        """Compiles term.

        integerConstant | stringConstant | keywordConstant | varName |
        varName '[' expression ']' | subroutineCall | '(' expression ')' |
        unaryOp term
        """

        if self._check_syntax("integerConstant"):
            self._write_checked_token("integerConstant")
        elif self._check_syntax("stringConstant"):
            self._write_checked_token("stringConstant")
        elif self._check_syntax(content=self.keyword_constant):
            self._write_checked_token(content=self.keyword_constant)
        elif self._check_syntax("identifier"):
            self._write_checked_token("identifier")
            if self._check_syntax("symbol", "["):
                self._write_checked_token("symbol", "[")
                self.compile_expression()
                self._write_checked_token("symbol", "]")
        elif self._check_syntax("symbol", "("):
            self._write_checked_token("symbol", "(")
            self.compile_expression()
            self._write_checked_token("symbol", ")")
        elif self._check_syntax("symbol", self.unary_ops):
            self._write_checked_token("symbol", self.unary_ops)
            self.compile_term()
        else:
            try:
                self.compile_subroutine_call()
            except SyntaxError:
                raise RuntimeError(
                    f"Unexpected token {self._token_list[self._index]}")

    def compile_subroutine_call(self) -> None:
        """Compiles subroutine call.

        subroutineName '(' expressionList ')' |
        (className|varName) '.' subroutineName '(' expressionList ')'
        """

        if self._check_syntax(content=self._class_names + self.var_names):
            self._write_checked_token(
                content=self._class_names + self.var_names)
            self._write_checked_token("symbol", ".")

        self._write_checked_token(content=self._subroutine_names)
        self._write_checked_token("symbol", "(")
        self.compile_expression_list()
        self._write_checked_token("symbol", ")")

    def compile_expression_list(self) -> None:
        """Compiles expression list.

        (expression (',' expression)* )?
        """

        try:
            self.compile_expression()
            while self._check_syntax("symbol", ","):
                self._write_checked_token("symbol", ",")
                self.compile_expression()
        except RuntimeError:
            return

    def _check_syntax(self, tag: str = "", content: Union[str, List[str]] = "",
                      raises: bool = False) -> bool:
        """Checks syntax of current token.

        Args:
            tag (str, optional): Expected tag.
            content (str or list[str], optional): Expected content.
            raises (bool, optional): Whether raises error.

        Returns:
            checked (bool): If `True`, current token is expected one.

        Raises:
            ValueError: If `tag` and `content` are empty string.
            SyntaxError: If `raises` is `True` and `tag` or `content` do not
                match the current tag or content respectively.
        """

        cur_tag, cur_content, _ = self._token_list[self._index].split(" ")
        cur_tag = cur_tag.strip("<>")

        if not tag and not content:
            raise ValueError("Both tag and content are empty.")

        flag = True
        if tag:
            flag &= cur_tag == tag
        if content:
            if isinstance(content, str):
                content = [content]
            flag &= any(cur_content == c for c in content)

        if not flag and raises:
            raise SyntaxError(
                f"Expected tag='{tag}' and content='{content}', but given "
                f"tag='{cur_tag}' and content='{cur_content}' at "
                f"line={self._index + 1}.")

        return flag

    def _write_checked_token(self, tag: str = "",
                             content: Union[str, List[str]] = "") -> str:
        """Writes current token with syntax check.

        Args:
            tag (str, optional): Expected tag.
            content (str or list[str], optional): Expected content.

        Returns:
            content (str): Current content.
        """

        self._check_syntax(tag, content, raises=True)

        _, res, _ = self._token_list[self._index].split(" ")
        self._code.append(self._token_list[self._index])
        self._index += 1

        return res
