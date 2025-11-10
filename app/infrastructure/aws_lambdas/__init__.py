from app.infrastructure.aws_lambdas.lambda_handler import router, list_movies, get_movie, create_movie, update_movie, \
    delete_movie

__all__ = [
    "router",
    "list_movies",
    "get_movie",
    "create_movie",
    "update_movie",
    "delete_movie",
]

