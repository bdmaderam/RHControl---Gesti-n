from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Sin valores por defecto: si falta una variable obligatoria la app no arranca.
    database_url: str
    jwt_secret: str = Field(min_length=16)
    cors_origins: str = "http://localhost:3000,http://localhost"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()