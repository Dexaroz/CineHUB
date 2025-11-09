from app.application.commands.update_movie import UpdateMovie
from app.application.unit_of_work import UnitOfWork
from app.domain.vo.rating import Rating

def update_movie_handler(command: UpdateMovie, uow: UnitOfWork) -> None:
    with uow:
        movie = uow.movies.get(command.movie_id)
        if not movie:
            raise ValueError(f"Movie with id {command.movie_id} not found")

        if 'rate' in command.payload:
            movie.change_rating(Rating(command.payload['rate']))
            payload_copy = command.payload.copy()
            del payload_copy['rate']
        else:
            payload_copy = command.payload

        if payload_copy:
            movie.update(**payload_copy)

        uow.movies.add(movie)
        uow.commit()
