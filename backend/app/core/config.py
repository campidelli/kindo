from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Kindo School Payments API"
    app_version: str = "1.0.0"
    log_level: str = "INFO"
    cors_origins: list[str] = ["*"]  # Allow all origins in development
    database_path: Path = Path(__file__).resolve().parent.parent / "data" / "kindo.db"
    environment: str = "development"  # development, staging, production

    def get_cors_origins(self) -> list[str]:
        """Return CORS origins based on environment."""
        if self.environment == "production":
            # In production, restrict to specific origins
            return [
                "https://kindo-frontend.onrender.com",
                "https://kindo.com",  # Add your domain here
            ]
        return self.cors_origins  # Use env config or default


settings = Settings()
