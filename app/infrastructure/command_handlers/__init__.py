from app.infrastructure.command_handlers.create_movie_command_handler import create_movie_handler
from app.infrastructure.command_handlers.delete_movie_command_handler import delete_movie_handler
from app.infrastructure.command_handlers.update_movie_command_handler import update_movie_handler

__all__ = [
    'create_movie_handler',
    'delete_movie_handler',
    'update_movie_handler'
]
