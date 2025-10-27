from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MovieDTO:
    title: Optional[str]
    genre: Optional[str]
    director: Optional[str]
    year: Optional[int]
    rate: Optional[int]
    poster: Optional[str]
    synopsis: Optional[str]
    duration: Optional[int]
