from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    """Render provides postgres:// or postgresql:// — SQLAlchemy needs psycopg driver."""
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://") :]
    elif url.startswith("postgresql://") and "+psycopg" not in url:
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://barber:barber@localhost:5432/barber"
    admin_username: str = "admin"
    admin_password: str = "changeme"
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
    booking_cutoff_hours: int = 2
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    otel_service_name: str = "barber-api"
    otel_exporter_otlp_endpoint: str | None = None
    log_level: str = "INFO"

    @model_validator(mode="after")
    def _normalize_db(self) -> "Settings":
        self.database_url = normalize_database_url(self.database_url)
        if self.otel_exporter_otlp_endpoint == "":
            self.otel_exporter_otlp_endpoint = None
        return self


settings = Settings()
