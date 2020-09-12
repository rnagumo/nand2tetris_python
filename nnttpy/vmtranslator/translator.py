
"""Translator from Jack VM code to Hack assemble code.

ref)
https://github.com/chrisshyi/VMTranslator/blob/master/src/main/Translator.java
https://medium.com/@yizhe87/from-nand-to-tetris-nand2tetris-project-7-8-e74e8e009e71
"""

from typing import Union, List

import pathlib

from nnttpy import vmtranslator


class VMTranslator:
    """Translator for VM code."""

    def __init__(self):

        self._parser = vmtranslator.VMParser()
        self._writer = vmtranslator.VMCodeWriter()

    def translate(self, path: Union[str, pathlib.Path]) -> List[str]:
        """Translate given VM codes.

        Args:
            path (str or pathlib.Path): Path to .vm file or folder containing
                multiple .vm files.

        Returns:
            code (list of str): Translated assemble code.

        Raises:
            ValueError: If given path specifies a single file and its suffix is
                not '.vm'.
        """

        input_path = pathlib.Path(path)
        if input_path.is_dir():
            files = list(input_path.glob("*.vm"))
        else:
            if input_path.suffix != ".vm":
                raise ValueError(f"Expected .vm file, but given {input_path}.")
            files = [input_path]

        for p in files:
            with p.open("r") as f:
                lines = f.readlines()
            self._parser.code = lines
            self._writer.line_num = 0
            self._writer.file_name = p.stem.upper()

            while True:
                if self._parser.is_invalid():
                    pass
                elif self._parser.is_arithmetic():
                    self._writer.write_arithmetic(self._parser.command)
                elif self._parser.is_pushpop():
                    self._writer.write_pushpop(
                        self._parser.command, self._parser.arg1,
                        self._parser.arg2)
                else:
                    raise NotImplementedError

                try:
                    self._parser.advance()
                    self._writer.line_num += 1
                except RuntimeError:
                    break

        return self._writer.code
