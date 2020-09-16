
from typing import Union, List, Tuple

import pathlib

from nnttpy import jackcompiler


class JackAnalyzer:
    """Analyzer for Jack lang."""

    def __init__(self):

        self._tokenizer = jackcompiler.JackTokenizer()
        self._engine = jackcompiler.CompilationEngine()

    def compile_xml(self, path: Union[str, pathlib.Path]) -> List[str]:
        """Compiles Jack lang code to XML.

        Args:
            path (str or pathlib.Path): Path to .jack file or folder containing
                multiple .jack files.

        Returns:
            compiled_code (list of str): Translated assemble code.

        Raises:
            ValueError: If given path does not specify .jack file.
        """

        input_path = pathlib.Path(path)
        if input_path.is_dir():
            files = list(input_path.glob("*.jack"))
        else:
            files = [input_path]

        if not files or any(".jack" not in str(p) for p in files):
            raise ValueError(f"Found not-Jack files: {files}")

        token_list: List[Tuple[int, str]] = []
        for p in files:
            with p.open("r") as f:
                lines = f.readlines()

            self._tokenizer.code = lines
            while True:
                try:
                    self._tokenizer.advance()
                except RuntimeError:
                    break

                parsed = self._tokenizer.current_xml
                line = self._tokenizer.current_line
                if parsed:
                    token_list.append((line, parsed))

        compiled_code = self._engine.compile(token_list)

        return compiled_code
