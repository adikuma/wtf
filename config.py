from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # openrouter config
    openrouter_api_key: str = ""
    openrouter_url: str = "https://openrouter.ai/api/v1/chat/completions"
    wtf_model: str = "openai/gpt-oss-120b"
    wtf_provider: str = "deepinfra/fp4"


settings = Settings()
