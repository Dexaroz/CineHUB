from app.application.dtos.movie_out import MovieOut
from app.domain.entities.movie import Movie

def _movie_to_dto(movie: Movie) -> MovieOut:
    return MovieOut(
        id=movie.id,
        title=movie.title,
        genre=movie.genre,
        director=movie.director,
        year=movie.year,
        rate=movie.rate.value,
        poster=movie.poster,
        synopsis=movie.synopsis,
        duration=movie.duration,
    )