from flask import Flask, jsonify

from app.api import bootstrap_message_bus
from app.api.routes import create_movies_blueprint
from app.config import settings

def create_app() -> Flask:
    app = Flask(__name__)

    app.config['JSON_SORT_KEYS'] = False
    app.config['DEBUG'] = settings.FLASK_DEBUG

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

    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,X-Api-Key'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        return response

    @app.route('/<path:path>', methods=['OPTIONS'])
    @app.route('/movies', methods=['OPTIONS'])
    @app.route('/movies/<path:path>', methods=['OPTIONS'])
    def handle_options(path=None):
        response = app.make_response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,X-Api-Key'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        return response, 204


    return app

app = create_app()

if __name__ == '__main__':
    port = int(getattr(settings, "PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=bool(getattr(settings, "FLASK_DEBUG", True)))