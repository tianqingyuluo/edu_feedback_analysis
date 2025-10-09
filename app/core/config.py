from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    analysis_file_path: str
    machine_learning_models_path: str
    analysis_task_path: str
    redis_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    log_level: str
    openai_api_key: str
    openai_embedding_api_key: str
    chat_openai_api_base: str
    embedding_openai_api_base: str
    llm_model_name: str
    embedding_model_name: str
    chroma_persist_path: str
    project_name: str
    version: str



    class Config:
        # env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file = ".env"

settings = Settings()