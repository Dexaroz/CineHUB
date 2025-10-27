from typing import Optional

from app.application.idProvider.idProvider import IdProvider
from app.application.movie.command.commands import CreateMovieCommand, UpdateMovieCommand, DeleteMovieCommand
from app.domain.movie.movie import Movie
from app.domain.movie.movieRepository import MovieRepository


class CreateMovieCommandHandler:
    def __init__(self, repo: MovieRepository, id_provider: IdProvider) -> None:
        self.repo = repo
        self.ids = id_provider

    def __call__(self, cmd: CreateMovieCommand) -> Movie:
        if not cmd.title or not cmd.title.strip():
            raise ValueError("title is required")
        if not (0 <= int(cmd.rate) <= 5):
            raise ValueError("rate must be 0..5")
        if not (1888 <= int(cmd.year) <= 2100):
            raise ValueError("year must be 1888..2100")
        if int(cmd.duration) <= 0:
            raise ValueError("duration must be > 0")

        entity = Movie(
            id=self.ids.next_id(),
            title=cmd.title.strip(),
            genre=cmd.genre.strip(),
            director=cmd.director.strip(),
            year=int(cmd.year),
            rate=int(cmd.rate),
            poster=cmd.poster.strip(),
            synopsis=cmd.synopsis.strip(),
            duration=int(cmd.duration),
        )
        return self.repo.add(entity)


class UpdateMovieCommandHandler:
    def __init__(self, repo: MovieRepository) -> None:
        self.repo = repo

    def __call__(self, cmd: UpdateMovieCommand) -> Optional[Movie]:
        current = self.repo.get(int(cmd.id))
        if current is None:
            return None
        if not cmd.title or not cmd.title.strip():
            raise ValueError("title is required")
        if not (0 <= int(cmd.rate) <= 5):
            raise ValueError("rate must be 0..5")
        if not (1888 <= int(cmd.year) <= 2100):
            raise ValueError("year must be 1888..2100")
        if int(cmd.duration) <= 0:
            raise ValueError("duration must be > 0")
        entity = Movie(
            id=int(cmd.id),
            title=cmd.title.strip(),
            genre=cmd.genre.strip(),
            director=cmd.director.strip(),
            year=int(cmd.year),
            rate=int(cmd.rate),
            poster=cmd.poster.strip(),
            synopsis=cmd.synopsis.strip(),
            duration=int(cmd.duration),
        )
        return self.repo.replace(entity)



class DeleteMovieCommandHandler:
    def __init__(self, repo: MovieRepository) -> None:
        self.repo = repo

    def __call__(self, cmd: DeleteMovieCommand) -> bool:
        return self.repo.delete(int(cmd.id))
