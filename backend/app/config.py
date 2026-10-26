from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://barber:barber@localhost:5432/barber"
    admin_username: str = "admin"
    admin_password: str = "changeme"
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
    booking_cutoff_hours: int = 2
    cors_origins: str = "http://localhost:5173"
    otel_service_name: str = "barber-api"
    otel_exporter_otlp_endpoint: str | None = None
    log_level: str = "INFO"


settings = Settings()
