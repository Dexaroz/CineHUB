from app.application.commands.delete_movie import DeleteMovie
from app.application.unit_of_work import UnitOfWork


def delete_movie_handler(command: DeleteMovie, uow: UnitOfWork) -> None:
    with uow:
        movie = uow.movies.get(command.movie_id)
        if not movie:
            raise ValueError(f"Movie with id {command.movie_id} not found")

        deleted = uow.movies.remove(command.movie_id)
        if not deleted:
            raise ValueError(f"Failed to delete movie with id {command.movie_id}")

        uow.commit()
