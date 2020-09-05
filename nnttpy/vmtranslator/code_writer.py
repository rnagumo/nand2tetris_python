
from typing import List


class CodeWriter:
    """Code writer of Hack assemble codes."""

    def __init__(self):

        self._code: List[str] = []

    def write_arithmetic(self, command: str) -> None:
        """"""

        raise NotImplementedError

    def write_pushpop(self, command: str, segment: str, index: int) -> None:
        """"""

        raise NotImplementedError
