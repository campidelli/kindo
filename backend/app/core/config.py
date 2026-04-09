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
    cors_origins: list[str] = ["*"]
    database_path: Path = Path(__file__).resolve().parent.parent / "data" / "kindo.db"


settings = Settings()
