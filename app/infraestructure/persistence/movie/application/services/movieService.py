from app.domain.movie.movieRepository import MovieRepository


class MovieService:
    def __init__(self, repo: MovieRepository) -> None:
        self.repo = repo
        self._seq = 0

    def next_id(self) -> int:
        self._seq += 1
        return self._seq