# lambda_handlers.py
import json
import os
from typing import Any, Dict, Optional

# ==== AJUSTA ESTOS IMPORTS A TU PROYECTO ====
# Commands / Queries
from app.application.commands.create_movie import CreateMovie
from app.application.commands.update_movie import UpdateMovie
from app.application.commands.delete_movie import DeleteMovie
from app.application.queries.get_movie import GetMovie
from app.application.queries.get_movies import GetMovies

from app.infrastructure.dynamodb_unit_of_work import DynamoDBUnitOfWork

from app.infrastructure.command_handlers.create_movie_command_handler import create_movie_handler
from app.infrastructure.command_handlers.update_movie_command_handler import update_movie_handler
from app.infrastructure.command_handlers.delete_movie_command_handler import delete_movie_handler
from app.infrastructure.queries_handlers.get_movie_query_handler import get_movie_handler
from app.infrastructure.queries_handlers.get_movies_query_handler import get_movies_handler
# ============================================

CORS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
}

def _resp(status: int, body: Any = None, extra_headers: Dict[str, str] | None = None):
    headers = {**CORS, **(extra_headers or {})}
    # Para 204 no enviar body
    if status == 204:
        return {"statusCode": 204, "headers": headers, "isBase64Encoded": False, "body": ""}
    return {
        "statusCode": status,
        "headers": headers,
        "isBase64Encoded": False,
        "body": json.dumps(body if body is not None else {}),
    }

def _json_body(event) -> Dict[str, Any]:
    raw = event.get("body")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise BadRequest("JSON inválido")

def _path_param(event, name: str) -> Optional[str]:
    return (event.get("pathParameters") or {}).get(name)

def _query(event) -> Dict[str, Any]:
    return event.get("queryStringParameters") or {}

class BadRequest(Exception): ...
class NotFound(Exception): ...
class Conflict(Exception): ...


def list_movies(event, _context):
    """
    GET /movies?title=&year=&genre=
    """
    filters = _query(event)
    with DynamoDBUnitOfWork() as uow:
        items = get_movies_handler(GetMovies(filters=filters), uow)
    return _resp(200, {"items": items})

def get_movie(event, _context):
    """
    GET /movies/{id}
    """
    movie_id = _path_param(event, "id")
    if movie_id is None:
        return _resp(400, {"error": "Falta path param 'id'"})
    with DynamoDBUnitOfWork() as uow:
        try:
            item = get_movie_handler(GetMovie(id=movie_id), uow)
            return _resp(200, item)
        except ValueError as e:
            # Tus handlers suelen lanzar ValueError para "no encontrado"
            return _resp(404, {"error": str(e)})

def create_movie(event, _context):
    """
    POST /movies
    Body JSON SIN 'id' (tu handler lo genera)
    """
    try:
        payload = _json_body(event)
    except BadRequest as e:
        return _resp(400, {"error": str(e)})

    with DynamoDBUnitOfWork() as uow:
        try:
            cmd = CreateMovie(payload=CreateMovie.Payload(**payload)) if hasattr(CreateMovie, "Payload") else CreateMovie(**payload)
            new_id = create_movie_handler(cmd, uow)
            return _resp(201, {"id": new_id}, extra_headers={"Location": f"/movies/{new_id}"})
        except TypeError as e:
            return _resp(400, {"error": f"Datos inválidos: {e}"})
        except Conflict as e:
            return _resp(409, {"error": str(e)})
        except Exception as e:
            msg = str(e)
            code = 409 if "duplicate" in msg.lower() or "exists" in msg.lower() else 400
            return _resp(code, {"error": msg})

def update_movie(event, _context):
    """
    PUT /movies/{id}
    """
    movie_id = _path_param(event, "id")
    if movie_id is None:
        return _resp(400, {"error": "Falta path param 'id'"})
    try:
        payload = _json_body(event)
    except BadRequest as e:
        return _resp(400, {"error": str(e)})

    with DynamoDBUnitOfWork() as uow:
        try:
            cmd = UpdateMovie(id=movie_id, payload=UpdateMovie.Payload(**payload)) if hasattr(UpdateMovie, "Payload") else UpdateMovie(id=movie_id, **payload)
            update_movie_handler(cmd, uow)
            return _resp(200, {"message": "Actualizado"})
        except ValueError as e:
            return _resp(404, {"error": str(e)})
        except TypeError as e:
            return _resp(400, {"error": f"Datos inválidos: {e}"})

def delete_movie(event, _context):
    """
    DELETE /movies/{id}
    """
    movie_id = _path_param(event, "id")
    if movie_id is None:
        return _resp(400, {"error": "Falta path param 'id'"})
    with DynamoDBUnitOfWork() as uow:
        try:
            cmd = DeleteMovie(id=movie_id)
            delete_movie_handler(cmd, uow)
            return _resp(204)
        except ValueError as e:
            return _resp(404, {"error": str(e)})


def router(event, context):
    """
    Punto de entrada (CMD) del contenedor/ZIP.
    Cada Lambda establece HANDLER_NAME en {list,get,create,update,delete}.
    """
    name = os.getenv("HANDLER_NAME", "").lower()
    if name == "list":   return list_movies(event, context)
    if name == "get":    return get_movie(event, context)
    if name == "create": return create_movie(event, context)
    if name == "update": return update_movie(event, context)
    if name == "delete": return delete_movie(event, context)
    return _resp(500, {"error": f"HANDLER_NAME '{name}' no soportado"})
