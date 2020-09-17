
from typing import Union, List, Tuple

import pathlib

from nnttpy import jackcompiler


class JackAnalyzer:
    """Analyzer for Jack lang."""

    def __init__(self):

        self._tokenizer = jackcompiler.JackTokenizer()
        self._engine = jackcompiler.XMLCompilationEngine()

    def compile_xml(self, path: Union[str, pathlib.Path]) -> List[str]:
        """Compiles Jack lang code to XML.

        Args:
            path (str or pathlib.Path): Path to .jack file.

        Returns:
            xml_code (list of str): Parsed XML code.

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

        xml_code = self._engine.compile(token_list)

        return xml_code
