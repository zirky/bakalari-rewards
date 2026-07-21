from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "change_me"
    BAKALARI_BASE_URL: str = ""
    BAKALARI_USERNAME: str = ""
    BAKALARI_PASSWORD: str = ""
    LNBITS_HOST: str = "https://lnbits.cz"
    LNBITS_ADMIN_KEY: str = ""
    LIGHTNING_ADDRESS: str = ""
    EXCHANGE_RATE_API_URL: str = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=czk"
    AUTO_PAYOUT: bool = False
    MOCK_MODE: bool = False
    START_DATE: str = "2024-09-01"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
