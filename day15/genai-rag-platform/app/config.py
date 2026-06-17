from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    AZURE_OPENAI_KEY: str
    AZURE_OPENAI_ENDPOINT: str

    CLAUDE_API_KEY: str

    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    class Config:
        env_file = ".env"

settings = Settings()