from dataclasses import dataclass

@dataclass
class Movie:
    id: int
    title: str
    genre: str
    director: str
    year: int
    rate: int
    poster: str
    synopsis: str
    duration: int
