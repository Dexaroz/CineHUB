from flask import jsonify, Flask
from flask_cors import CORS

from app.api.bootstrap import bootstrap_message_bus
from app.api.routes.movies import create_movies_blueprint
from app.config import settings

def create_app() -> Flask:
    app = Flask(__name__)

    app.config['JSON_SORT_KEYS'] = False
    app.config['DEBUG'] = settings.FLASK_DEBUG

    CORS(app, resources={r"/*": {"origins": "*"}})

    bus = bootstrap_message_bus()

    app.register_blueprint(create_movies_blueprint(bus))

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'}), 200

    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'Movies API',
            'version': '1.0.0',
            'endpoints': {
                'health': 'GET /health',
                'list_movies': 'GET /movies',
                'get_movie': 'GET /movies/<id>',
                'create_movie': 'POST /movies',
                'update_movie': 'PUT/PATCH /movies/<id>',
                'delete_movie': 'DELETE /movies/<id>',
            }
        }), 200

    return app