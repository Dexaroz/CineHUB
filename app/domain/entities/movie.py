from dataclasses import dataclass
from app.domain.vo.rating import Rating

@dataclass
class Movie:
    id: int
    title: str
    genre: str
    director: str
    year: int
    rate: Rating
    poster: str
    synopsis: str
    duration: int

    def change_rating(self, rating: Rating) -> None:
        self.rate = rating

    def update(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)