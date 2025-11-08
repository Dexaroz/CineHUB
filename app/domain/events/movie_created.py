from dataclasses import dataclass


@dataclass(frozen=True)
class MovieCreated:
    movie_id: int
