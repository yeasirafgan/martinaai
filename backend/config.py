from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Martinaai"
    version: str = "1.0.0"
    claude_api_key: str = ""
    model: str = "claude-sonnet-4-6"
    allowed_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
