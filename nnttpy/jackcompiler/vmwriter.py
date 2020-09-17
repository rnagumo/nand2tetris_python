
from typing import List


class VMWriter:
    """VM writer in compilation."""

    memory_segment = ["argument", "local", "static", "constant", "this",
                      "that", "pointer", "temp"]
    op_commands = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]

    def __init__(self):

        self._code: List[str] = []

    def write_push(self, segment: str, index: int) -> None:
        """Writes push methods `push segment index`.

        Args:
            segment (str): Segment of variable.
            index (int): Index of memory.

        Raises:
            ValueError: If `segment` is not one in `memory_segment`.
        """

        if segment not in self.memory_segment:
            raise ValueError(f"Unexpected segment: {segment}")

        raise NotImplementedError

    def write_pop(self, segment: str, index: int) -> None:
        """Writes pop methods `pop segment index`.

        Args:
            segment (str): Segment of variable.
            index (int): Index of memory.

        Raises:
            ValueError: If `segment` is not one in `memory_segment`.
        """

        if segment not in self.memory_segment:
            raise ValueError(f"Unexpected segment: {segment}")

        raise NotImplementedError

    def write_arithmetic(self, command: str) -> None:
        """Writes arithmetic command.

        Args:
            command (str): Arithmetic command.

        Raises:
            ValueError: If `command` is not one in `op_commands`.
        """

        if command not in self.op_commands:
            raise ValueError(f"Unexpected command: {command}")

        raise NotImplementedError

    def write_label(self, label: str) -> None:
        """Writes label command `label 'label'`.

        Args:
            label (str): Label of code.
        """

        raise NotImplementedError

    def write_goto(self, label: str) -> None:
        """Writes goto command `goto 'label'`.

        Args:
            label (str): Label of code.
        """

        raise NotImplementedError

    def write_if(self, label: str) -> None:
        """Writes if-goto command `if-goto 'label'`.

        Args:
            label (str): Label of code.
        """

        raise NotImplementedError

    def write_call(self, name: str, n_args: int) -> None:
        """Writes function call `call 'name' 'a_args'`.

        Args:
            name (str): String of name.
            n_args (int): Number of arguments.
        """

        raise NotImplementedError

    def write_function(self, name: str, n_locals: int) -> None:
        """Writes function statements `function 'name' 'n_locals'`.

        Args:
            name (str): String of function name.
            n_locals (int): Number of local variables.
        """

        raise NotImplementedError

    def write_return(self) -> None:
        """Writes return commands `return`."""

        raise NotImplementedError
