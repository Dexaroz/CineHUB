from typing import Dict

from app.domain.movie.movie import Movie
from app.sharedKernel.repository import Repository

class MovieRepository(Repository[Movie, int]):
    def __init__(self) -> None:
        self._db: Dict[int, Movie] = {}

    def list(self, q: str | None = None) -> list[Movie]:
        items = list(self._db.values())
        if q:
            ql = q.lower()
            items = [
                m for m in items
                if ql in f"{m.title} {m.genre} {m.director}".lower()
            ]
        return items

    def get(self, entity_id: int) -> Movie | None:
        return self._db.get(entity_id)

    def add(self, entity: Movie) -> Movie:
        if entity.id in self._db:
            raise ValueError(f"Movie with id={entity.id} already exists")
        self._db[entity.id] = entity
        return entity

    def update(self, entity: Movie) -> Movie | None:
        if entity.id not in self._db:
            return None
        self._db[entity.id] = entity
        return entity

    def delete(self, entity_id: int) -> bool:
        return self._db.pop(entity_id, None) is not None
