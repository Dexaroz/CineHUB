from app.application.commands.create_movie import CreateMovie
from app.application.commands.delete_movie import DeleteMovie
from app.application.commands.update_movie import UpdateMovie
from app.application.queries.get_movie import GetMovie
from app.application.queries.get_movies import GetMovies
from app.infraestructure.command_handlers.create_movie_command_handler import create_movie_handler
from app.infraestructure.command_handlers.delete_movie_command_handler import delete_movie_handler
from app.infraestructure.command_handlers.update_movie_command_handler import update_movie_handler
from app.infraestructure.queries_handlers.get_movie_query_handler import get_movie_handler
from app.infraestructure.queries_handlers.get_movies_query_handler import get_movies_handler
from app.service.message_bus import MessageBus


def bootstrap_message_bus() -> MessageBus:
    bus = MessageBus()

    bus.register_command_handler(CreateMovie, create_movie_handler)
    bus.register_command_handler(UpdateMovie, update_movie_handler)
    bus.register_command_handler(DeleteMovie, delete_movie_handler)

    bus.register_query_handler(GetMovie, get_movie_handler)
    bus.register_query_handler(GetMovies, get_movies_handler)

    return bus