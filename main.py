from app.app import create_app
from app.config import settings

app = create_app()

if __name__ == '__main__':
    port = int(getattr(settings, "PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=bool(getattr(settings, "FLASK_DEBUG", True)))