from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Automated Content Factory"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    OPENAI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    REDIS_URL: str = "redis://localhost:6379/0"
    VECTOR_DB_URL: str = "http://localhost:8000"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:latest"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # LLM Routing (cloud fallback when Ollama is unavailable)
    LLM_CLOUD_ENABLED: bool = True
    OPENAI_FALLBACK_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_FALLBACK_MODEL: str = "claude-3-5-haiku-latest"
    LLM_CIRCUIT_FAILURE_THRESHOLD: int = 3
    LLM_CIRCUIT_RECOVERY_SECONDS: float = 300.0

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
