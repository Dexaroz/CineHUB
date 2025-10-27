from typing import Dict, List, Optional

from app.domain.movie.movie import Movie


class InMemoryMovieRepository:
    def __init__(self) -> None:
        self._db: Dict[int, Movie] = {}

    def list(self, q: str | None = None) -> List[Movie]:
        items = list(self._db.values())
        if q:
            ql = q.lower().strip()
            items = [m for m in items if ql in f"{m.title} {m.genre} {m.director}".lower()]
        return items

    def get(self, movie_id: int) -> Optional[Movie]:
        return self._db.get(movie_id)

    def add(self, entity: Movie) -> Movie:
        if entity.id in self._db:
            raise ValueError("duplicate id")
        self._db[entity.id] = entity
        return entity

    def replace(self, entity: Movie) -> Optional[Movie]:
        if entity.id not in self._db:
            return None
        self._db[entity.id] = entity
        return entity

    def delete(self, movie_id: int) -> bool:
        return self._db.pop(movie_id, None) is not None