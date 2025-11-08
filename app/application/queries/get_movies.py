from dataclasses import dataclass

@dataclass(frozen=True)
class GetMovies:
    genre: str | None = None
    director: str | None = None
    search: str | None = None