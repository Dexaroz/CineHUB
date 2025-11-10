import json
from typing import Any, Dict, Optional

from app.application.commands.create_movie import CreateMovie
from app.application.commands.update_movie import UpdateMovie
from app.application.commands.delete_movie import DeleteMovie
from app.application.queries.get_movie import GetMovie
from app.application.queries.get_movies import GetMovies
from app.application.dtos.movie_in import MovieIn

from app.infrastructure.dynamodb_unit_of_work import DynamoDBUnitOfWork
from app.service.message_bus import MessageBus

from app.infrastructure.command_handlers.create_movie_command_handler import create_movie_handler
from app.infrastructure.command_handlers.update_movie_command_handler import update_movie_handler
from app.infrastructure.command_handlers.delete_movie_command_handler import delete_movie_handler
from app.infrastructure.queries_handlers.get_movie_query_handler import get_movie_handler
from app.infrastructure.queries_handlers.get_movies_query_handler import get_movies_handler

message_bus = MessageBus()
message_bus.register_command_handler(CreateMovie, create_movie_handler)
message_bus.register_command_handler(UpdateMovie, update_movie_handler)
message_bus.register_command_handler(DeleteMovie, delete_movie_handler)
message_bus.register_query_handler(GetMovie, get_movie_handler)
message_bus.register_query_handler(GetMovies, get_movies_handler)

CORS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
}

def _resp(status: int, body: Any = None, extra_headers: Dict[str, str] | None = None):
    headers = {**CORS, **(extra_headers or {})}
    if status == 204:
        return {"statusCode": 204, "headers": headers, "isBase64Encoded": False, "body": ""}
    return {
        "statusCode": status,
        "headers": headers,
        "isBase64Encoded": False,
        "body": json.dumps(body or {}, default=str),
    }

def _json_body(event) -> Dict[str, Any]:
    raw = event.get("body")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return _resp(400, {"error": "JSON inválido"})

def _path_param(event, name: str) -> Optional[str]:
    return (event.get("pathParameters") or {}).get(name)

def _query(event) -> Dict[str, Any]:
    return event.get("queryStringParameters") or {}

def list_movies(event, _context):

    query_params = _query(event)
    query = GetMovies(
        genre=query_params.get("genre"),
        director=query_params.get("director"),
        search=query_params.get("search"),
    )
    uow = DynamoDBUnitOfWork()
    try:
        movies = message_bus.handle_query(query, uow)
        items = [m.model_dump() for m in movies]
        return _resp(200, items)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return _resp(500, {"error": f"Error retrieving movies: {str(e)}"})

def get_movie(event, _context):
    movie_id = _path_param(event, "id")
    if movie_id is None:
        return _resp(400, {"error": "Falta path param 'id'"})
    try:
        movie_id_int = int(movie_id)
    except ValueError:
        return _resp(400, {"error": "ID debe ser un número"})
    query = GetMovie(movie_id=movie_id_int)
    uow = DynamoDBUnitOfWork()
    try:
        movie = message_bus.handle_query(query, uow)
        return _resp(200, movie.model_dump())
    except ValueError as e:
        import traceback
        traceback.print_exc()
        return _resp(404, {"error": str(e)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return _resp(500, {"error": f"Error retrieving movie: {str(e)}"})

def create_movie(event, _context):
    parsed = _json_body(event)
    if isinstance(parsed, dict) and "statusCode" in parsed:
        return parsed
    if not parsed:
        return _resp(400, {"error": "No data provided"})
    try:
        rate_in = parsed.get("rate", parsed.get("rating"))
        duration_in = parsed.get("duration", parsed.get("runtime"))

        required_missing = []
        for f in ("title", "year", "genre", "director", "poster", "synopsis"):
            if not parsed.get(f):
                required_missing.append(f)
        if rate_in is None:
            required_missing.append("rating (o rate)")
        if duration_in is None:
            required_missing.append("runtime (o duration)")
        if required_missing:
            return _resp(400, {"error": f"Faltan campos: {', '.join(required_missing)}"})

        try:
            rate_val = int(float(rate_in))
        except Exception:
            return _resp(400, {"error": "Campo 'rating/rate' debe ser numérico"})
        try:
            duration_val = int(duration_in)
        except Exception:
            return _resp(400, {"error": "Campo 'runtime/duration' debe ser entero"})

        movie_in = MovieIn(
            title=parsed["title"],
            year=int(parsed["year"]),
            genre=parsed["genre"],
            director=parsed["director"],
            rate=rate_val,
            duration=duration_val,
            synopsis=parsed["synopsis"],
            poster=parsed["poster"],
        )
    except KeyError as e:
        return _resp(400, {"error": f"Campo requerido faltante: {str(e)}"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return _resp(400, {"error": f"Validation error: {str(e)}"})

    command = CreateMovie(payload=movie_in)
    uow = DynamoDBUnitOfWork()
    try:
        movie_id = message_bus.handle_command(command, uow)
        return _resp(
            201,
            {"id": movie_id, "message": "Movie created successfully"},
            extra_headers={"Location": f"/movies/{movie_id}"},
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return _resp(500, {"error": f"Error creating movie: {str(e)}"})

def update_movie(event, _context):
    movie_id = _path_param(event, "id")
    if movie_id is None:
        return _resp(400, {"error": "Falta path param 'id'"})
    try:
        movie_id_int = int(movie_id)
    except ValueError:
        return _resp(400, {"error": "ID debe ser un número"})

    parsed = _json_body(event)
    if isinstance(parsed, dict) and "statusCode" in parsed:
        return parsed
    if not parsed:
        return _resp(400, {"error": "No data provided"})

    payload: Dict[str, Any] = {}
    if "title" in parsed:
        payload["title"] = parsed["title"]
    if "year" in parsed:
        try:
            payload["year"] = int(parsed["year"])
        except Exception:
            return _resp(400, {"error": "Campo 'year' debe ser entero"})
    if "genre" in parsed:
        payload["genre"] = parsed["genre"]
    if "director" in parsed:
        payload["director"] = parsed["director"]

    if "rate" in parsed or "rating" in parsed:
        rate_in = parsed.get("rate", parsed.get("rating"))
        try:
            payload["rate"] = int(float(rate_in))
        except Exception:
            return _resp(400, {"error": "Campo 'rating/rate' debe ser numérico"})
    if "duration" in parsed or "runtime" in parsed:
        duration_in = parsed.get("duration", parsed.get("runtime"))
        try:
            payload["duration"] = int(duration_in)
        except Exception:
            return _resp(400, {"error": "Campo 'runtime/duration' debe ser entero"})

    if "synopsis" in parsed:
        payload["synopsis"] = parsed["synopsis"]
    if "poster" in parsed:
        payload["poster"] = parsed["poster"]

    command = UpdateMovie(movie_id=movie_id_int, payload=payload)
    uow = DynamoDBUnitOfWork()
    try:
        message_bus.handle_command(command, uow)
        return _resp(200, {"message": "Movie updated successfully"})
    except ValueError as e:
        import traceback
        traceback.print_exc()
        return _resp(404, {"error": str(e)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return _resp(500, {"error": f"Error updating movie: {str(e)}"})

def delete_movie(event, _context):
    movie_id = _path_param(event, "id")
    if movie_id is None:
        return _resp(400, {"error": "Falta path param 'id'"})
    try:
        movie_id_int = int(movie_id)
    except ValueError:
        return _resp(400, {"error": "ID debe ser un número"})

    command = DeleteMovie(movie_id=movie_id_int)
    uow = DynamoDBUnitOfWork()
    try:
        message_bus.handle_command(command, uow)
        return _resp(204)
    except ValueError as e:
        import traceback
        traceback.print_exc()
        return _resp(404, {"error": str(e)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return _resp(500, {"error": f"Error deleting movie: {str(e)}"})

def router(event, context):
    import os
    name = os.getenv("HANDLER_NAME", "").lower()
    if name == "list":
        return list_movies(event, context)
    if name == "get":
        return get_movie(event, context)
    if name == "create":
        return create_movie(event, context)
    if name == "update":
        return update_movie(event, context)
    if name == "delete":
        return delete_movie(event, context)
    return _resp(500, {"error": f"HANDLER_NAME '{name}' no soportado"})
