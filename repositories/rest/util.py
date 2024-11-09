from typing import Protocol


class TokenProvider(Protocol):
    def get_token(self) -> str: ...  # pragma: no cover
