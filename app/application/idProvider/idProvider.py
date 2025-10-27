from typing import Protocol


class IdProvider(Protocol):
    def next_id(self) -> int: ...