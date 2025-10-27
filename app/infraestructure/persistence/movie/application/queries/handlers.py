from typing import Optional

from app.application.movie.query.query import GetAll, GetMovie
from app.domain.movie.movie import Movie
from app.domain.movie.movieRepository import MovieRepository


class GetAllQueryHandler:
    def __init__(self, repo: MovieRepository) -> None:
        self.repo = repo

    def __call__(self, qry: GetAll) -> list[Movie]:
        return self.repo.list(qry.q)

class GetMovieQueryHandler:
    def __init__(self, repo: MovieRepository) -> None:
        self.repo = repo

    def __call__(self, qry: GetMovie) -> Optional[Movie]:
        return self.repo.get(int(qry.id))
