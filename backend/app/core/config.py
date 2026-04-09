from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Kindo School Payments API"
    app_version: str = "1.0.0"
    log_level: str = "INFO"
    cors_origins: list[str] = ["*"]
    database_path: str = "app/data/kindo.db"
    environment: str = "development"

    def get_cors_origins(self) -> list[str]:
        """Return CORS origins from configuration."""
        return self.cors_origins


settings = Settings()
