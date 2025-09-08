import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    analysis_file_path: str
    machine_learning_models_path: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    log_level: str
    project_name: str
    version: str



    class Config:
        # env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file = ".env"

settings = Settings()