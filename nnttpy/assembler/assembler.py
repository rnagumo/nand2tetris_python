
from typing import List, Dict

from nnttpy import assembler


class Assembler:
    """Hack assembler."""

    predefined_symbols = {
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4,
        "SCREEN": 16384,
        "KBD": 24576,
    }
    ram_predefined = 16

    def __init__(self, code: List[str]):

        self.parser = assembler.Parser(code)
        self.converter = assembler.Converter()
        self.symbol_table: Dict[str, str] = {}

    def assemble(self) -> List[str]:
        """Assembles given code.

        1. Create symbol table.
        2. Convert assemble code to binary.

        Returns:
            binary (list[str]): Binarized code.
        """

        self._create_symbol_table()
        binary = self._convert_code()
        return binary

    def _create_symbol_table(self) -> None:

        _symbol_table: Dict[str, int] = self.predefined_symbols.copy()

        # Add pre-defined symbol in RAM
        for n in range(self.ram_predefined):
            _symbol_table[f"R{n}"] = n

        # Add label symbol with ROM address
        rom_address = 0
        while True:
            if self.parser.is_a_cmd() or self.parser.is_c_cmd():
                rom_address += 1
            elif self.parser.is_l_cmd():
                symbol = self.parser.symbol()
                if symbol not in _symbol_table:
                    _symbol_table[symbol] = rom_address
                else:
                    raise ValueError(f"Duplicated label symbol: {symbol}.")

            try:
                self.parser.advance()
            except RuntimeError:
                break

        # Convert int -> bin string
        for key, value in _symbol_table.items():
            self.symbol_table[key] = f"{format(value, 'b'):0>15}"

    def _convert_code(self) -> List[str]:

        self.parser.reset_index()

        res = []
        ram_address = self.ram_predefined
        while True:
            binary = ""
            if self.parser.is_invalid() or self.parser.is_l_cmd():
                pass
            elif self.parser.is_c_cmd():
                binary += "111"
                binary += "1" if "M" in self.parser.comp() else "0"
                binary += self.converter.comp(self.parser.comp())
                binary += self.converter.dest(self.parser.dest())
                binary += self.converter.jump(self.parser.jump())
            elif self.parser.is_a_cmd():
                binary += "0"
                symbol = self.parser.symbol()
                if not all("0" <= c <= "9" for c in symbol):
                    if symbol not in self.symbol_table:
                        self.symbol_table[symbol] = (
                            f"{format(ram_address, 'b'):0>15}")
                        ram_address += 1
                    symbol = self.symbol_table[symbol]
                binary += symbol
            else:
                raise ValueError(
                        f"Unknown command type {self.parser.command_type}.")

            if binary:
                res.append(binary)

            try:
                self.parser.advance()
            except RuntimeError:
                break

        return res
