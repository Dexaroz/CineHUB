from flasgger import Swagger
from flask import Flask
from flask_cors import CORS

from app.application.idProvider.MovieIdProvider import MemoryIdProvider
from app.application.movie.command.commands import CreateMovieCommand, UpdateMovieCommand, DeleteMovieCommand
from app.application.movie.query.query import GetAll, GetMovie
from app.controller.movieController import MovieController, create_movie_blueprint
from app.infraestructure.persistence.movie.application.commands.handlers import CreateMovieCommandHandler, \
    UpdateMovieCommandHandler, DeleteMovieCommandHandler
from app.infraestructure.persistence.movie.application.memoryRepository import InMemoryMovieRepository
from app.infraestructure.persistence.movie.application.queries.handlers import GetAllQueryHandler, GetMovieQueryHandler
from app.sharedKernel.cqrs import CommandBus, QueryBus
from app.sharedKernel.errors import register_error_handlers


def get_swagger_config():
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "CineHUB API",
            "description": "CRUD de películas con Hexagonal + DDD + CQRS",
            "version": "1.0.0"
        },
        "basePath": "/",
        "schemes": ["http"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "definitions": {
            "Movie": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "title": {"type": "string"},
                    "genre": {"type": "string"},
                    "director": {"type": "string"},
                    "year": {"type": "integer"},
                    "rate": {"type": "integer", "minimum": 0, "maximum": 5},
                    "poster": {"type": "string"},
                    "synopsis": {"type": "string"},
                    "duration": {"type": "integer"}
                },
                "required": ["id","title","genre","director","year","rate","poster","synopsis","duration"]
            },
            "MovieCreate": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "genre": {"type": "string"},
                    "director": {"type": "string"},
                    "year": {"type": "integer"},
                    "rate": {"type": "integer", "minimum": 0, "maximum": 5},
                    "poster": {"type": "string"},
                    "synopsis": {"type": "string"},
                    "duration": {"type": "integer"}
                },
                "required": ["title","genre","director","year","rate","poster","synopsis","duration"]
            }
        }
    }
    swagger_cfg = {
        "headers": [],
        "openapi": "2.0",
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
    }
    return swagger_template, swagger_cfg

def register_handlers(command_bus, query_bus, repo, ids):
    command_bus.register(CreateMovieCommand, CreateMovieCommandHandler(repo, ids))
    command_bus.register(UpdateMovieCommand, UpdateMovieCommandHandler(repo))
    command_bus.register(DeleteMovieCommand, DeleteMovieCommandHandler(repo))

    query_bus.register(GetAll, GetAllQueryHandler(repo))
    query_bus.register(GetMovie, GetMovieQueryHandler(repo))


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    CORS(app, resources={r"/*": {"origins": "*"}})

    repo = InMemoryMovieRepository()
    ids = MemoryIdProvider()
    command_bus = CommandBus()
    query_bus = QueryBus()
    register_handlers(command_bus, query_bus, repo, ids)

    controller = MovieController(command_bus, query_bus)
    app.register_blueprint(create_movie_blueprint(controller), url_prefix="/movies")

    @app.get("/health")
    def health():
        return {"ok": True}

    register_error_handlers(app)
    template, cfg = get_swagger_config()
    Swagger(app, template=template, config=cfg)

    return app
