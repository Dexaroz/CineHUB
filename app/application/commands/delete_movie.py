from dataclasses import dataclass

@dataclass(frozen=True)
class DeleteMovie:
    movie_id: int