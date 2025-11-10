from app.application.commands.create_movie import CreateMovie
from app.application.id_generator.id_incremental_generator import id_generator
from app.application.unit_of_work import UnitOfWork
from app.domain.entities.movie import Movie
from app.domain.vo.rating import Rating


def create_movie_handler(command: CreateMovie, uow: UnitOfWork) -> int:
    with uow:
        movie_id = id_generator.generate()

        movie = Movie(
            id=movie_id,
            title=command.payload.title,
            genre=command.payload.genre,
            director=command.payload.director,
            year=command.payload.year,
            rate=Rating(command.payload.rate),
            poster=command.payload.poster,
            synopsis=command.payload.synopsis,
            duration=command.payload.duration,
        )

        uow.movies.add(movie)
        uow.commit()

        return movie_id