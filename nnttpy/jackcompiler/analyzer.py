
from typing import Union, List

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
            code (list of str): Translated assemble code.

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

        res: List[str] = ["<tokens>"]
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
                if parsed:
                    res.append(parsed)

        res.append("</tokens>")
        return res
