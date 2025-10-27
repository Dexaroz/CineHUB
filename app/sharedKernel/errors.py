from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(err):
        return jsonify({"error": getattr(err, "description", "Bad Request")}), 400

    @app.errorhandler(404)
    def not_found(err):
        return jsonify({"error": getattr(err, "description", "Not Found")}), 404

    @app.errorhandler(422)
    def unprocessable(err):
        return jsonify({"error": getattr(err, "description", "Unprocessable Entity")}), 422

    @app.errorhandler(500)
    def server_error(_):
        return jsonify({"error": "Internal Server Error"}), 500
