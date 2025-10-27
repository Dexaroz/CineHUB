from flask import Blueprint, request, jsonify, abort
from app.sharedKernel.cqrs import CommandBus, QueryBus
from app.application.movie.command.commands import CreateMovieCommand, UpdateMovieCommand, DeleteMovieCommand
from app.application.movie.query.query import GetAll, GetMovie

REQUIRED = ["title","genre","director","year","rate","poster","synopsis","duration"]

class MovieController:
    def __init__(self, commands: CommandBus, queries: QueryBus):
        self.commands = commands
        self.queries  = queries

    def list(self):
        """
        Get all movies
        ---
        tags: [movies]
        parameters:
          - in: query
            name: q
            type: string
            required: false
            description: Texto de búsqueda (título/género/director)
        responses:
          200:
            description: OK
            schema:
              type: array
              items:
                $ref: '#/definitions/Movie'
        """
        q = request.args.get("q")
        items = self.queries.ask(GetAll(q=q))
        return jsonify([m.__dict__ for m in items])

    def get(self, movie_id: int):
        """
        Get movie by id
        ---
        tags: [movies]
        parameters:
          - in: path
            name: movie_id
            type: integer
            required: true
        responses:
          200:
            description: OK
            schema:
              $ref: '#/definitions/Movie'
          404:
            description: Movie not found
        """
        m = self.queries.ask(GetMovie(id=movie_id))
        if not m: abort(404, description="Movie not found")
        return jsonify(m.__dict__)

    def create(self):
        """
        Create movie
        ---
        tags: [movies]
        parameters:
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/MovieCreate'
        responses:
          201:
            description: Created
            schema:
              $ref: '#/definitions/Movie'
          400:
            description: Validation error
        """
        p = _ensure_json()
        created = self.commands.handle(CreateMovieCommand(**_require_all(p)))
        return jsonify(created.__dict__), 201

    def update(self, movie_id: int):
        """
               Replace movie (PUT)
               ---
               tags: [movies]
               parameters:
                 - in: path
                   name: movie_id
                   type: integer
                   required: true
                 - in: body
                   name: body
                   required: true
                   schema:
                     $ref: '#/definitions/MovieCreate'
               responses:
                 200:
                   description: Updated
                   schema:
                     $ref: '#/definitions/Movie'
                 404:
                   description: Movie not found
               """
        p = _ensure_json()
        updated = self.commands.handle(UpdateMovieCommand(id=movie_id, **_require_all(p)))
        if not updated: abort(404, description="Movie not found")
        return jsonify(updated.__dict__)

    def delete(self, movie_id: int):
        """
                Delete movie
                ---
                tags: [movies]
                parameters:
                  - in: path
                    name: movie_id
                    type: integer
                    required: true
                responses:
                  200:
                    description: Deleted
                    schema:
                      type: object
                      properties:
                        deleted:
                          type: integer
                  404:
                    description: Movie not found
                """
        ok = self.commands.handle(DeleteMovieCommand(id=movie_id))
        if not ok: abort(404, description="Movie not found")
        return jsonify({"deleted": movie_id})

def _ensure_json() -> dict:
    from flask import request
    try:
        data = request.get_json(force=True, silent=False)
        if not isinstance(data, dict):
            abort(400, description="JSON object required")
        return data
    except Exception as e:
        abort(400, description=f"Invalid JSON: {e}")

def _require_all(p: dict) -> dict:
    missing = [k for k in REQUIRED if k not in p]
    if missing: abort(400, description=f"Missing fields: {', '.join(missing)}")
    return {k: p[k] for k in REQUIRED}

def create_movie_blueprint(controller: MovieController) -> Blueprint:
    bp = Blueprint("movie", __name__)
    bp.add_url_rule("/",              view_func=controller.list,   methods=["GET"])
    bp.add_url_rule("/<int:movie_id>",view_func=controller.get,    methods=["GET"])
    bp.add_url_rule("/",              view_func=controller.create, methods=["POST"])
    bp.add_url_rule("/<int:movie_id>",view_func=controller.update, methods=["PUT"])
    bp.add_url_rule("/<int:movie_id>",view_func=controller.delete, methods=["DELETE"])
    return bp
