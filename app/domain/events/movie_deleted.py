from dataclasses import dataclass

@dataclass(frozen=True)
class MovieDeleted:
    movie_id: int