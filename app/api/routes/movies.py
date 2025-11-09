import traceback

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.application.commands.create_movie import CreateMovie
from app.application.commands.delete_movie import DeleteMovie
from app.application.commands.update_movie import UpdateMovie
from app.application.dtos.movie_in import MovieIn
from app.application.queries.get_movie import GetMovie
from app.application.queries.get_movies import GetMovies
from app.infrastructure.dynamodb_unit_of_work import DynamoDBUnitOfWork
from app.service.message_bus import MessageBus


def create_movies_blueprint(bus: MessageBus) -> Blueprint:
    movies_bp = Blueprint('movies', __name__, url_prefix='/movies')

    @movies_bp.route('', methods=['GET'])
    def list_movies():
        """
        GET /movies - List all movies
        GET /movies?genre=Action - Filter by genre
        GET /movies?director=Nolan - Filter by director
        GET /movies?search=inception - Search in title and synopsis
        """
        genre = request.args.get('genre')
        director = request.args.get('director')
        search = request.args.get('search')

        query = GetMovies(genre=genre, director=director, search=search)
        uow = DynamoDBUnitOfWork()

        try:
            movies = bus.handle_query(query, uow)
            return jsonify([movie.model_dump() for movie in movies]), 200
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': f'Error retrieving movies: {str(e)}'}), 500

    @movies_bp.route('/<int:movie_id>', methods=['GET'])
    def get_movie(movie_id: int):
        """GET /movies/{id} - Get a specific movie"""
        query = GetMovie(movie_id=movie_id)
        uow = DynamoDBUnitOfWork()

        try:
            movie = bus.handle_query(query, uow)
            return jsonify(movie.model_dump()), 200
        except ValueError as e:
            traceback.print_exc()
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': f'Error retrieving movie: {str(e)}'}), 500

    @movies_bp.route('', methods=['POST'])
    def create_movie():
        """POST /movies - Create a new movie"""
        if not request.json:
            return jsonify({'error': 'No data provided'}), 400

        try:
            movie_in = MovieIn(**request.json)
        except ValidationError as e:
            traceback.print_exc()
            return jsonify({'error': e.errors()}), 400

        command = CreateMovie(payload=movie_in)
        uow = DynamoDBUnitOfWork()

        try:
            movie_id = bus.handle_command(command, uow)
            return jsonify({
                'id': movie_id,
                'message': 'Movie created successfully'
            }), 201
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': f'Error creating movie: {str(e)}'}), 500

    @movies_bp.route('/<int:movie_id>', methods=['PUT', 'PATCH'])
    def update_movie(movie_id: int):
        """
        PUT /movies/{id} - Update a movie (full update)
        """
        if not request.json:
            return jsonify({'error': 'No data provided'}), 400

        command = UpdateMovie(movie_id=movie_id, payload=request.json)
        uow = DynamoDBUnitOfWork()

        try:
            bus.handle_command(command, uow)
            return jsonify({'message': 'Movie updated successfully'}), 200
        except ValueError as e:
            traceback.print_exc()
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': f'Error updating movie: {str(e)}'}), 500

    @movies_bp.route('/<int:movie_id>', methods=['DELETE'])
    def delete_movie(movie_id: int):
        """DELETE /movies/{id} - Delete a movie"""
        command = DeleteMovie(movie_id=movie_id)
        uow = DynamoDBUnitOfWork()

        try:
            bus.handle_command(command, uow)
            return jsonify({'message': 'Movie deleted successfully'}), 200
        except ValueError as e:
            traceback.print_exc()
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': f'Error deleting movie: {str(e)}'}), 500

    return movies_bp