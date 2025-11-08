from dataclasses import dataclass

@dataclass(frozen=True)
class GetMovie:
    movie_id: int