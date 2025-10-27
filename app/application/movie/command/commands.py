from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateMovieCommand:
    title: str
    genre: str
    director: str
    year: int
    rate: int
    poster: str
    synopsis: str
    duration: int

@dataclass(frozen=True)
class UpdateMovieCommand:
    id: int
    title: Optional[str]
    genre: Optional[str]
    director: Optional[str]
    year: Optional[int]
    rate: Optional[int]
    poster: Optional[str]
    synopsis: Optional[str]
    duration: Optional[int]

@dataclass(frozen=True)
class DeleteMovieCommand:
    id: int