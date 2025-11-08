from pydantic import BaseModel
import os

class Settings(BaseModel):
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    DDB_TABLE_NAME: str = os.getenv("DDB_TABLE_NAME", "MoviesTable")
    DDB_ENDPOINT_URL: str | None = os.getenv("DDB_ENDPOINT_URL")
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() == "true"

settings = Settings()
