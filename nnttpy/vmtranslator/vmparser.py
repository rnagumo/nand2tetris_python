
from typing import List


class VMParser:
    """Parser for VM code."""

    # Command type
    c_invalid = 0
    c_arithmetic = 1
    c_push = 2
    c_pop = 3
    c_label = 4
    c_goto = 5
    c_if = 6
    c_function = 7
    c_return = 8
    c_call = 9

    def __init__(self):

        self._code: List[str] = []
        self._length = 0
        self._index = 0
        self._current = ""

    @property
    def code(self) -> List[str]:
        return self._code

    @code.setter
    def code(self, code: List[str]) -> None:
        self._code = code
        self._length = len(code)
        self._index = 0
        self.advance()

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

        if not self.has_more_commands():
            raise RuntimeError("No successive command exists.")

        # Remove comments
        # ex) "D=A  // comment" -> "D=A"
        self._current = self._code[self._index].split("//")[0].strip()
        self._index += 1

    @property
    def command_type(self) -> int:
        """Command type.

        Returns:
            command_type (int): parsed current command type.

        Raises:
            ValueErorr: If unexpected command is given.
        """

        if not self._current:
            return self.c_invalid

        command = self._current.split(" ")[0]
        if command == "push":
            return self.c_push
        elif command == "pop":
            return self.c_pop
        elif command == "label":
            return self.c_label
        elif command == "goto":
            return self.c_goto
        elif command == "if-goto":
            return self.c_if
        elif command == "function":
            return self.c_function
        elif command == "return":
            return self.c_return
        elif command == "call":
            return self.c_call
        elif (command in
                ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]):
            return self.c_arithmetic

        raise ValueError(f"Unexpected command: {self._current}")

    def is_invalid(self) -> bool:
        return self.command_type == self.c_invalid

    def is_pushpop(self) -> bool:
        return self.command_type in [self.c_push, self.c_pop]

    def is_arithmetic(self) -> bool:
        return self.command_type == self.c_arithmetic

    @property
    def command(self) -> str:
        """Returns current command.

        Returns:
            command (str): Parsed command.
        """

        command, *_ = self._current.split(" ")
        return command

    @property
    def arg1(self) -> str:
        """First argument of current command.

        Returns:
            arg1 (str): Parsed argument.

        Raises:
            AttributeError: If `command_type` is not expected one.
        """

        if self.command_type == self.c_return:
            raise AttributeError(f"Invalid command type: {self.command_type}")

        if self.command_type == self.c_arithmetic:
            return self._current

        _, arg1, *_ = self._current.split(" ")
        return arg1

    @property
    def arg2(self) -> str:
        """Second argument of current command.

        Returns:
            arg2 (str): Parsed argument.

        Raises:
            AttributeError: If `command_type` is not expected one.
        """

        if (self.command_type not in
                [self.c_push, self.c_pop, self.c_function, self.c_call]):
            raise AttributeError(f"Invalid command type: {self.command_type}")

        *_, arg2 = self._current.split(" ")
        return arg2
