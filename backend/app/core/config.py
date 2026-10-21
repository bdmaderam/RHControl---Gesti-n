from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://rhcontrol:rhcontrol@db:5432/rhcontrol"
    jwt_secret: str = "clave-local-rhcontrol-cambiar-en-produccion"
    cors_origins: str = "http://localhost:3000,http://localhost"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
