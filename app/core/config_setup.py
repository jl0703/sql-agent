from langchain_openai.chat_models import AzureChatOpenAI

from app.core.config import settings


LLM = AzureChatOpenAI(
    openai_api_key=settings.AZURE_OPENAI_API_KEY.get_secret_value(),
    openai_api_version=settings.AZURE_OPENAI_API_VERSION,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
    max_tokens=settings.MAX_TOKENS,
    temperature=settings.TEMPERATURE,
    seed=settings.SEED,
)

CONN_STRING: str = (
    f"dbname={settings.POSTGRES_DB} "
    f"user={settings.POSTGRES_USER} "
    f"password={settings.POSTGRES_PASSWORD.get_secret_value()} "
    f"host={settings.POSTGRES_SERVER} "
    f"port={settings.POSTGRES_PORT}"
)
