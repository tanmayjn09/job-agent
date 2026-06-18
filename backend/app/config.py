from pydantic_settings import BaseSettings
from pydantic import field_validator
from pathlib import Path


class Settings(BaseSettings):
    anthropic_api_key: str
    serpapi_key: str = ""
    database_url: str = "sqlite:///./job_agent.db"

    @field_validator("database_url", mode="before")
    @classmethod
    def database_url_nonempty(cls, v):
        if not v or not str(v).strip():
            return "sqlite:///./job_agent.db"
        return v
    upload_dir: str = str(Path(__file__).parent.parent.parent.parent / "uploads")
    secret_key: str = "change-this-in-production"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    frontend_url: str = ""
    crunchbase_api_key: str = ""
    hunter_api_key: str = ""

    @property
    def all_cors_origins(self) -> list[str]:
        origins = list(self.cors_origins)
        if self.frontend_url and self.frontend_url not in origins:
            origins.append(self.frontend_url)
        return origins

    class Config:
        env_file = ".env"


settings = Settings()
