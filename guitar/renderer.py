from typing import Protocol

import typer
from rich.console import Console


class Renderer(Protocol):
    def print(self, msg: str) -> None: ...
    def prompt(self, msg: str) -> str: ...
    def confirm(self, msg: str, default: bool = True) -> bool: ...


class RichRenderer:  # pragma: no cover
    def __init__(self) -> None:
        self._console = Console()

    def print(self, msg: str) -> None:
        self._console.print(msg)

    def prompt(self, msg: str) -> str:
        return str(typer.prompt(msg)) if msg else (input() or "")

    def confirm(self, msg: str, default: bool = True) -> bool:
        return bool(typer.confirm(msg, default=default))
