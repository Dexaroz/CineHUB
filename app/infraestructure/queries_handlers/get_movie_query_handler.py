from app.application.dtos.movie_out import MovieOut
from app.application.dtos.movie_to_dto import _movie_to_dto
from app.application.queries.get_movie import GetMovie
from app.application.unit_of_work import UnitOfWork


def get_movie_handler(query: GetMovie, uow: UnitOfWork) -> MovieOut:
    with uow:
        movie = uow.movies.get(query.movie_id)
        if not movie:
            raise ValueError(f"Movie with id {query.movie_id} not found")
        return _movie_to_dto(movie)
