
from typing import List


class Parser:
    """Pasrser class for assemble code."""

    # Command type of parsed code
    invalid = 0
    a_command = 1
    c_command = 2
    l_command = 3

    # Candidate for mnemonic
    comp_cand = set(["0", "1", "-1", "D", "A", "!D", "!A", "-D", "-A", "D+1",
                     "A+1", "D-1", "A-1", "D+A", "D-A", "A-D", "D&A", "D|A",
                     "M", "!M", "-M", "M+1", "M-1", "D+M", "D-M", "M-D", "D&M",
                     "D|M"])
    dest_cand = set(["M", "D", "MD", "A", "AM", "AD", "AMD"])
    jump_cand = set(["JGT", "JEQ", "JGE", "JLT", "JNE", "JLE", "JMP"])

    def __init__(self, code: List[str]):

        self._code = code
        self._length = len(code)
        self._index = 0
        self._current = ""

        # Set first command
        self.advance()

    @property
    def has_more_commands(self) -> bool:
        """Check whether command exists in input.

        Returns:
            has (bool): Command existence.
        """

        return self._index < self._length

    def advance(self) -> None:
        """Go to the next command.

        Raises:
            RuntimeError: If `has_more_commands` is `False`.
        """

        if not self.has_more_commands:
            raise RuntimeError("No successive command exists.")

        # Remove comments
        # ex) "D=A  // comment" -> "D=A"
        self._current = self._code[self._index].split("//")[0].strip()
        self._index += 1

    def reset_index(self) -> None:
        """Reset index to top."""

        self._index = 0
        self.advance()

    @property
    def command_type(self) -> int:
        """Command type.

        Returns:
            command_type (int): Invalid = 0, Address = 1, Compute = 2,
                Location = 3.
        """

        if not self._current:
            return self.invalid
        elif self._current[0] == "@":
            return self.a_command
        elif self._current[0] == "(" and self._current[-1] == ")":
            return self.l_command
        return self.c_command

    def is_invalid(self) -> bool:
        """Checks command type."""
        return self.command_type == self.invalid

    def is_a_cmd(self) -> bool:
        """Checks command type."""
        return self.command_type == self.a_command

    def is_l_cmd(self) -> bool:
        """Checks command type."""
        return self.command_type == self.l_command

    def is_c_cmd(self) -> bool:
        """Checks command type."""
        return self.command_type == self.c_command

    def symbol(self) -> str:
        """Get symbol.

        Returns:
            symbol (str): Symbol of 15-bits.

        Raises:
            AttributeError: If `command_type` is not `a_command` nor
                `l_command`.
        """

        if (self.command_type != self.a_command
                and self.command_type != self.l_command):
            raise AttributeError(f"Invalid command type: {self.command_type}")

        symbol = self._current.strip("@()")
        if all("0" <= c <= "9" for c in symbol):
            symbol = f"{format(int(symbol), 'b'):0>15}"

        return symbol

    def comp(self) -> str:
        """Returns comp mnemonic.

        Returns:
            comp (str): comp mnemonic.

        Raises:
            AttributeError: If `command_type` is not `c_command`.
            ValueError: If parsed comp command is not one of the expected.
        """

        if self.command_type != self.c_command:
            raise AttributeError(f"Invalid command type: {self.command_type}")

        comp = self._current.split("=")[-1].split(";")[0].strip()
        if comp not in self.comp_cand:
            raise ValueError(f"Unknown comp command '{comp}'.")
        return comp

    def dest(self) -> str:
        """Returns dest mnemonic.

        Returns:
            dest (str): dest mnemonic.

        Raises:
            AttributeError: If `command_type` is not `c_command`.
            ValueError: If parsed dest command is not one of the expected.
        """

        if self.command_type != self.c_command:
            raise AttributeError(f"Invalid command type: {self.command_type}")

        if "=" not in self._current:
            return "null"

        dest = self._current.split("=")[0].strip()
        if dest not in self.dest_cand:
            raise ValueError(f"Unknown dest command '{dest}'.")

        return dest

    def jump(self) -> str:
        """Returns jump mnemonic.

        Returns:
            jump (str): jump mnemonic.

        Raises:
            AttributeError: If `command_type` is not `c_command`.
            ValueError: If parsed jump command is not one of the expected.
        """

        if self.command_type != self.c_command:
            raise AttributeError(f"Invalid command type: {self.command_type}")

        if ";" not in self._current:
            return "null"

        jump = self._current.split(";")[1].strip()
        if jump not in self.jump_cand:
            raise ValueError(f"Unknown jump command '{jump}'.")

        return jump
