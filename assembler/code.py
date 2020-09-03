
class Converter:
    """Convert all mnemonics to binary codes."""

    comp_table = {
        "0": "101010",
        "1": "111111",
        "-1": "111010",
        "D": "001100",
        "A": "110000",
        "!D": "001101",
        "!A": "110001",
        "-D": "001111",
        "-A": "110011",
        "D+1": "011111",
        "A+1": "110111",
        "D-1": "001110",
        "A-1": "110010",
        "D+A": "000010",
        "D-A": "010011",
        "A-D": "000111",
        "D&A": "000000",
        "D|A": "010101",
        "M": "110000",
        "!M": "110001",
        "-M": "110011",
        "M+1": "110111",
        "M-1": "110010",
        "D+M": "000010",
        "D-M": "010011",
        "M-D": "000111",
        "D&M": "000000",
        "D|M": "010101",
    }

    dest_table = {
        "null": "000",
        "M": "001",
        "D": "010",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "AD": "110",
        "AMD": "111",
    }

    jump_table = {
        "null": "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111",
    }

    def comp(self, mnemonic: str) -> str:
        """Converts comp mnemonic to binary code.

        Args:
            mnemonic (str): comp command.

        Returns:
            binary (str): Converted binary code.
        """

        return self.comp_table[mnemonic]

    def dest(self, mnemonic: str) -> str:
        """Converts dest mnemonic to binary code.

        Args:
            mnemonic (str): dest command.

        Returns:
            binary (str): Converted binary code.
        """

        return self.dest_table[mnemonic]

    def jump(self, mnemonic: str) -> str:
        """Converts jump mnemonic to binary code.

        Args:
            mnemonic (str): jump command.

        Returns:
            binary (str): Converted binary code.
        """

        return self.jump_table[mnemonic]
