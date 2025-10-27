import os

class Settings:
    PORT = int(os.getenv("PORT", "8080"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")