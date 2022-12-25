from pydantic import BaseSettings


class Settings(BaseSettings):
    debug = True
    database_habits: str
    BACKEND: str
    AUTH_SERVICE: str

    class Config:
        env_file = ".env"