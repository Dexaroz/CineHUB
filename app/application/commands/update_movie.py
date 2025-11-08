from dataclasses import dataclass

@dataclass(frozen=True)
class UpdateMovie:
    movie_id: int
    payload: dict