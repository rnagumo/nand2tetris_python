
from typing import List


class CodeWriter:
    """Code writer of Hack assemble codes."""

    # Templates
    end_program = ["(END)", "@END", "0;JMP"]
    inc_sp = ["@SP", "M=M+1"]
    dec_sp = ["@SP", "M=M-1", "A=M"]
    op_table = {
        "add": "+",
        "sub": "-",
        "neg": "-",
        "eq": "=",
        "gt": ">",
        "lt": "<",
        "and": "&",
        "or": "|",
        "not": "!",
    }
    jump_cmd = set(["JGT", "JEQ", "JGE", "JLT", "JNE", "JLE", "JMP"])

    def __init__(self):

        self._code: List[str] = []

    @property
    def code(self) -> str:
        """Returns wrote codes. This method should be called at last."""

        if not self._code:
            raise ValueError("Empty code.")

        if len(self._code) < 3 or self._code[-3:] != self.end_program:
            self._code += self.end_program

        return "\n".join(self._code)

    def write_arithmetic(self, command: str) -> None:
        """"""

        has_args = command in ["neg", "not"]
        self._pop_stack()
        if has_args:
            self._pop_stack()
        self._code += [f"D={'M' if has_args else ''}{self.op_table[command]}D"]

        if command == "eq":
            self._jump("JEQ")
        elif command == "gt":
            self._jump("JGT")
        elif command == "lt":
            self._jump("JLT")

        raise NotImplementedError

    def write_pushpop(self, command: str, segment: str, index: int) -> None:
        """"""

        raise NotImplementedError

    def _push_stack(self, constant: str = "") -> None:

        if constant:
            self._code += [f"@{constant}", "D=A"]
        self._code += ["@SP", "A=M", "M=D"]
        self._code += self.inc_sp

    def _pop_stack(self, save_to_d: bool = False) -> None:

        self._code += self.dec_sp
        if save_to_d:
            self._code += ["D=M"]

    def _jump(self, jump_type: str) -> None:

        if jump_type not in self.jump_cmd:
            raise ValueError(f"Invalid jump type: {jump_type}")

        self._code += ["@TRUE_JUMP", f"D;{jump_type}", "D=0"]
        self._code += ["@FALSE_NO_JUMP", "0;JMP"]
        self._code += ["(TRUE_JUMP)", "D=-1", "(FALSE_NO_JUMP)"]
