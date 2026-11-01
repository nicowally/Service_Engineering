from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Liest die Konfiguration aus Umgebungsvariablen bzw. der .env-Datei."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    sql_echo: bool = False


settings = Settings()
"fertiges objekt, welches den Inhalt von Settings() für andere Files speichert und abgerufen wird"