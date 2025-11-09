from typing import List
from app.application.dtos.movie_out import MovieOut
from app.application.dtos.movie_to_dto import _movie_to_dto
from app.application.queries.get_movies import GetMovies
from app.application.unit_of_work import UnitOfWork


def get_movies_handler(query: GetMovies, uow: UnitOfWork) -> List[MovieOut]:
    with uow:
        movies = uow.movies.list(
            genre=query.genre,
            director=query.director,
            search=query.search,
        )
        return [_movie_to_dto(movie) for movie in movies]