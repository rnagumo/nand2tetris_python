
from typing import Dict

import dataclasses


@dataclasses.dataclass
class TableElement:
    name: str = ""
    type: str = ""
    kind: str = ""
    number: int = -1


class SymbolTable:
    """Symbol table class."""

    possible_kind = ["static", "field", "argument", "var"]

    def __init__(self):

        self._class_table: Dict[str, TableElement] = {}
        self._subroutine_table: Dict[str, TableElement] = {}
        self._number_table: Dict[str, int] = {k: 0 for k in self.possible_kind}

    def __repr__(self) -> str:

        res = []
        res.append("Class table")
        for key, value in self._class_table.items():
            res.append(f"  {key}: {dataclasses.asdict(value)}")

        res.append("Subroutine table")
        for key, value in self._subroutine_table.items():
            res.append(f"  {key}: {dataclasses.asdict(value)}")

        return "\n".join(res)

    def __getitem__(self, key: str) -> TableElement:
        """Gets symbol attributes from table.

        Args:
            key (str): Name of the symbol.

        Returns:
            element (TableElement): Element of the symbol. If symbol of the
                given key is not found in table, an empty element is returned.
        """

        if key in self._class_table:
            element = self._class_table[key]
        elif key in self._subroutine_table:
            element = self._subroutine_table[key]
        else:
            raise KeyError(f"Not found key: {key}")

        return element

    def __contains__(self, key: str) -> bool:
        """Returns whether the specified key exists in table.

        Args:
            key (str): Name of the symbol.

        Returns:
            res (bool): Key exists or not in table.
        """

        try:
            _ = self.__getitem__(key)
        except KeyError:
            return False

        return True

    def start_class(self) -> None:
        """Resets class table at the start of class."""

        self._class_table = {}
        self._number_table["static"] = 0
        self._number_table["field"] = 0
        self.start_subroutine()

    def start_subroutine(self) -> None:
        """Resets subroutine table at the start of subroutine."""

        self._subroutine_table = {}
        self._number_table["arg"] = 0
        self._number_table["var"] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines new symbol.

        Args:
            name (str): Name of new symbol.
            type (str): Type of new symbol.
            kind (str): Kind of new symbol.
        """

        if kind not in self.possible_kind:
            raise ValueError(f"Unexpected kind '{kind}'.")

        if not name or not type:
            raise ValueError(
                f"Empty string is not allowed: name={name}, type={type}")

        number = self._number_table[kind]
        self._number_table[kind] += 1

        if kind in ["static", "field"]:
            self._class_table[name] = TableElement(
                name=name, type=type, kind=kind, number=number)
        else:
            self._subroutine_table[name] = TableElement(
                name=name, type=type, kind=kind, number=number)
