from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    llm_provider: str = "anthropic"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    embedding_provider: str = "openai"          # openai | stub
    openai_embedding_model: str = "text-embedding-3-small"
    cohere_api_key: str = ""
    database_url: str = "postgresql://postgres:postgres@localhost:5432/rfp"
    allowed_origins: str = "*"   # comma-separated; set to your Vercel URL in production
    org_profile_path: str = "profile.json"
    chunk_max_tokens: int = 900
    retrieval_top_k: int = 8

settings = Settings()
