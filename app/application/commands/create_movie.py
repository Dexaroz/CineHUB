from dataclasses import dataclass
from app.application.dtos.movie_in import MovieIn


@dataclass(frozen=True)
class CreateMovie:
    payload: MovieIn