from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    anthropic_api_key: str
    serpapi_key: str = ""
    database_url: str = "sqlite:///./job_agent.db"
    upload_dir: str = str(Path(__file__).parent.parent.parent.parent / "uploads")
    secret_key: str = "change-this-in-production"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
