
from typing import Union, List, Tuple

import pathlib

from nnttpy import jackcompiler


class JackAnalyzer:
    """Analyzer for Jack lang."""

    def __init__(self):

        self._tokenizer = jackcompiler.JackTokenizer()
        self._xml_engine = jackcompiler.XMLCompilationEngine()
        self._engine = jackcompiler.JackCompileEngine()

    def compile_xml(self, path: Union[str, pathlib.Path]) -> List[str]:
        """Compiles Jack lang code to XML.

        Args:
            path (str or pathlib.Path): Path to .jack file.

        Returns:
            xml_code (list of str): Parsed XML code.
        """

        token_list = self._tokenize_code(path)
        try:
            xml_code = self._xml_engine.compile(token_list)
        except SyntaxError as e:
            raise SyntaxError(f"{e.msg} in {path}.") from e

        return xml_code

    def compile(self, path: Union[str, pathlib.Path]) -> List[str]:
        """Compiles Jack lang code to VM code.

        Args:
            path (str or pathlib.Path): Path to .jack file.

        Returns:
            vm_code (list of str): Parsed VM code.
        """

        token_list = self._tokenize_code(path)
        try:
            vm_code = self._engine.compile(token_list)
        except SyntaxError as e:
            raise SyntaxError(f"{e.msg} in {path}.") from e

        return vm_code

    def _tokenize_code(self, path: Union[str, pathlib.Path]
                       ) -> List[Tuple[int, str]]:
        """Tokenizes given jack file to Tokens.

        Args:
            path (str or pathlib.Path): Path to .jack file.

        Returns:
            xml_code (list of str): Parsed tokens.

        Raises:
            ValueError: If given path does not specify .jack file.
        """

        input_path = pathlib.Path(path)
        if input_path.suffix != ".jack":
            raise ValueError(f"Given file {input_path} is not .jack file.")

        with input_path.open("r") as f:
            lines = f.readlines()

        self._tokenizer.code = lines
        token_list: List[Tuple[int, str]] = []
        while True:
            try:
                self._tokenizer.advance()
            except RuntimeError:
                break

            parsed = self._tokenizer.current_xml
            line = self._tokenizer.current_line
            if parsed:
                token_list.append((line, parsed))

        return token_list
