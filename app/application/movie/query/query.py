from dataclasses import dataclass


@dataclass(frozen=True)
class GetAll:
    q: str | None = None

@dataclass(frozen=True)
class GetMovie:
    id: int