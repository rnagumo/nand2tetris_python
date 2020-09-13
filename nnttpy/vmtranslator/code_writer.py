
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
        self._func_count = 1
        self._arg_count = 0

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

    def write_push(self, segment: str, index: str) -> None:
        """Writes push command.

        Args:
            command (str): Command name (push or pop).
            segment (str): 1st argument, segment.
        """

        if segment == "constant":
            self._push_stack(index)
        elif segment == "static":
            self._load_static(index, push=True)
            self._push_stack()
        else:
            self._load_memory(segment, index)
            self._push_stack()

    def write_pop(self, segment: str, index: str) -> None:
        """Writes pop command.

        Args:
            command (str): Command name (push or pop).
            segment (str): 1st argument, segment.
        """

        self._pop_stack()
        if segment == "static":
            self._load_static(index, push=False)
        else:
            self._code += ["@13", "M=D"]
            self._load_memory(segment, index, save_from_r13=True)

    def write_init(self) -> None:
        """Initializes code."""

        self._arg_count = 0
        self._code += ["@256", "D=A", "@SP", "M=D"]
        self._init_function()
        self._code += ["@Sys.init", "0;JMP", f"(RETURN{self._func_count - 1})"]

    def write_label(self, label: str) -> None:
        """Writes label command.

        Args:
            label (str): Name of label.
        """

        self._code += [f"@{label}"]

    def write_goto(self, label: str) -> None:
        """Writes goto command.

        Args:
            label (str): Label of destination.
        """

        self._code += [f"@{label}", "0;JMP"]

    def write_if(self, label: str) -> None:
        """Writes if-goto command.

        Args:
            label (str): Label of destination.
        """

        self._pop_stack()
        self._code += [f"@{label}", "D;JNE"]

    def write_call(self, segment: str, index: str) -> None:
        """Writes call method.

        Args:
            segment (str): 1st argument, segment.
            index (str): 2nd argument, number of index.
        """

        self._arg_count = int(index)
        self._init_function()
        self._code += [f"@{segment}", f"(RETURN{self._func_count - 1})"]

    def write_return(self) -> None:
        """Writes return command."""

        self._code += ["@5", "D=A", "@LCL", "A=M-D", "D=M", "@15", "M=D"]
        self._pop_stack()
        self._code += ["@ARG", "A=M", "M=D", "D=A+1", "@SP", "M=D"]

        for register in ["THAT", "THIS", "ARG", "LCL"]:
            self._code += ["@LCL", "AM=M-1", "D=M", f"@{register}", "M=D"]

        self._code += ["@15", "A=M", "0;JMP"]

    def write_function(self, func_name: str, num_locals: str) -> None:
        """Writes funciton commadn.

        Args:
            func_name (str): Name of cuntion.
            num_locals (str): Number of local args.
        """

        self._code += [f"@{func_name}"]
        for _ in range(int(num_locals)):
            self._code += ["@0", "D=A"]
            self._push_stack()

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

    def _load_memory(self, segment: str, index: str,
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

    def _init_function(self) -> None:

        self._code += [f"@RETURN{self._func_count}", "D=A"]
        self._push_stack()
        for register in ["LCL", "ARG", "THIS", "THAT"]:
            self._code += [f"@{register}", "D=M"]
            self._push_stack()

        self._code += [f"@{self._arg_count + 5}", "D=A", "@SP", "D=M-D",
                       "@ARG", "M=D", "SP", "D=M", "LCL", "M=D"]
        self._func_count += 1
