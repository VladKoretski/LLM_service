from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # === GigaChat OAuth credentials ===
    gigachat_client_id: str = Field(..., alias="GIGACHAT_CLIENT_ID")
    gigachat_client_secret: str = Field(..., alias="GIGACHAT_CLIENT_SECRET")
    
    # === GigaChat optional settings ===
    gigachat_scope: str = Field(default="GIGACHAT_API_PERS", alias="GIGACHAT_SCOPE")
    gigachat_base_url: str = Field(default="https://gigachat.devices.sberbank.ru/api/v1", alias="GIGACHAT_BASE_URL")
    
    # === App settings ===
    llm_model_name: str = Field(default="GigaChat:latest", alias="LLM_MODEL")
    llm_timeout: int = Field(default=30, alias="LLM_TIMEOUT")
    cache_ttl_seconds: int = Field(default=300, alias="CACHE_TTL_SECONDS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = {
        "env_file": ".env", 
        "env_file_encoding": "utf-8",
        "extra": "ignore"  # Игнорировать неизвестные переменные, чтобы не падало
    }

settings = Settings()