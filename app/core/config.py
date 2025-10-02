from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Azure Chat OpenAI Configuration
    AZURE_OPENAI_API_KEY: SecretStr = Field(..., repr=False)
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_DEPLOYMENT: str
    AZURE_OPENAI_API_VERSION: str = "2023-05-15"
    MAX_TOKENS: int = 16000
    TEMPERATURE: int = 0
    SEED: int = 42

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr = Field(..., repr=False)
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    class Config:
        env_file = ".env"


settings = Settings()
