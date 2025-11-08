from dataclasses import dataclass

@dataclass(frozen=True)
class MovieUpdated:
    movie_id: int