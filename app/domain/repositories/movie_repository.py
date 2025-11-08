from abc import ABC, abstractmethod
from typing import Optional, Iterable
from app.domain.entities.movie import Movie


class MovieRepository(ABC):
    @abstractmethod
    def add(self, movie: Movie) -> None: ...

    @abstractmethod
    def get(self, movie_id: int) -> Optional[Movie]: ...

    @abstractmethod
    def remove(self, movie_id: int) -> None: ...

    @abstractmethod
    def list(
            self,
            *,
            genre: str | None = None,
            director: str | None = None,
            search: str | None = None,
    ) -> Iterable[Movie]: ...