class FakeRenderer:
    def __init__(self, responses: list[str] | None = None) -> None:
        self._responses = list(responses or [])
        self.printed: list[str] = []

    def print(self, msg: str) -> None:
        self.printed.append(msg)

    def prompt(self, msg: str) -> str:
        return self._responses.pop(0) if self._responses else ""

    def confirm(self, msg: str, default: bool = True) -> bool:
        return default
