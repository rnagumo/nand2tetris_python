
from typing import List


class VMCodeWriter:
    """Code writer of Hack assemble codes."""

    # Templates
    end_program = ["(END)", "@END", "0;JMP"]
    op_table = {
        "add": "+",
        "sub": "-",
        "neg": "-",
        "eq": "-",
        "gt": "-",
        "lt": "-",
        "and": "&",
        "or": "|",
        "not": "!",
    }
    jump_cmd = set(["JGT", "JEQ", "JGE", "JLT", "JNE", "JLE", "JMP"])
    symbol_hash = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT",
        "pointer": "THIS",
        "temp": "5",
    }

    def __init__(self):

        self._code: List[str] = []
        self.line_num = 0
        self.file_name = ""

    @property
    def code(self) -> List[str]:
        """Returns wrote codes. This method should be called at last."""

        if not self._code:
            raise ValueError("Empty code.")

        if len(self._code) < 3 or self._code[-3:] != self.end_program:
            self._code += self.end_program

        return self._code

    def write_arithmetic(self, command: str) -> None:
        """Writes arithmetic operation.

        Args:
            command (str): Command name.
        """

        has_args = command not in ["neg", "not"]
        self._pop_stack()
        if has_args:
            self._pop_stack(save_to_d=False)
        self._code += [f"D={'M' if has_args else ''}{self.op_table[command]}D"]

        if command == "eq":
            self._jump("JEQ")
        elif command == "gt":
            self._jump("JGT")
        elif command == "lt":
            self._jump("JLT")

        self._push_stack()

    def write_pushpop(self, command: str, segment: str, index: str) -> None:
        """Writes push/pop command.

        Args:
            command (str): Command name (push or pop).
            segment (str): 1st argument, segment.
            index (str): 2nd argument, number of index.

        Raises:
            ValueError: If given `command` is not 'push' nor 'pop'.
        """

        if command == "push":
            if segment == "constant":
                self._push_stack(index)
            elif segment == "static":
                self._load_static(index, push=True)
                self._push_stack()
            else:
                self._load_memory(segment, index, push=True)
                self._push_stack()
        elif command == "pop":
            self._pop_stack()
            if segment == "static":
                self._load_static(index, push=False)
            else:
                self._code += ["@13", "M=D"]
                self._load_memory(
                    segment, index, push=False, save_from_r13=True)
        else:
            raise ValueError(f"Unexpected command type: {command}")

    def _push_stack(self, constant: str = "") -> None:

        if constant:
            self._code += [f"@{constant}", "D=A"]
        self._code += ["@SP", "A=M", "M=D"]
        self._code += ["@SP", "M=M+1"]

    def _pop_stack(self, save_to_d: bool = True) -> None:

        self._code += ["@SP", "M=M-1", "A=M"]
        if save_to_d:
            self._code += ["D=M"]

    def _jump(self, jump_type: str) -> None:

        if jump_type not in self.jump_cmd:
            raise ValueError(f"Invalid jump type: {jump_type}")

        self._code += [
            f"@TRUE_JUMP.{self.file_name}.{self.line_num}",
            f"D;{jump_type}", "D=0"]
        self._code += [
            f"@FALSE_NO_JUMP.{self.file_name}.{self.line_num}", "0;JMP"]
        self._code += [
            f"(TRUE_JUMP.{self.file_name}.{self.line_num})", "D=-1",
            f"(FALSE_NO_JUMP.{self.file_name}.{self.line_num})"]

    def _load_static(self, index: str, push: bool) -> None:

        self._code += [f"@{self.file_name}.{index}"]
        if push:
            self._code += ["D=M"]
        else:
            self._code += ["M=D"]

    def _load_memory(self, segment: str, index: str, push: bool,
                     save_from_r13: bool = False) -> None:

        self._code += [f"@{index}", "D=A", f"@{self.symbol_hash[segment]}"]
        if segment in ["temp", "pointer"]:
            self._code += ["AD=A+D"]
        else:
            self._code += ["AD=M+D"]

        if save_from_r13:
            self._code += ["@14", "M=D", "@13", "D=M", "@14", "A=M", "M=D"]
        else:
            self._code += ["D=M"]
