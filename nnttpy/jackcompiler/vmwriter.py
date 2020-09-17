
from typing import List


class VMWriter:
    """VM writer in compilation."""

    def __init__(self):

        self._code: List[str] = []

    def write_push(self, segment: str, index: int) -> None:
        raise NotImplementedError

    def write_pop(self, segment: str, index: int) -> None:
        raise NotImplementedError

    def write_arithmetic(self, command: str) -> None:
        raise NotImplementedError

    def write_label(self, label: str) -> None:
        raise NotImplementedError

    def write_goto(self, label: str) -> None:
        raise NotImplementedError

    def write_if(self, label: str) -> None:
        raise NotImplementedError

    def write_call(self, name: str, n_args: int) -> None:
        raise NotImplementedError

    def write_function(self, name: str, n_locals: int) -> None:
        raise NotImplementedError

    def write_return(self) -> None:
        raise NotImplementedError
