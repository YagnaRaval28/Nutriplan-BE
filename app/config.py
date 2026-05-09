from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database
    PG_HOST: str = "localhost"
    PG_PORT: int = 5432
    PG_DBNAME: str = "nutriplan"
    PG_USER: str = "postgres"
    PG_PASSWORD: str
    DATABASE_URL: str = ""

    def model_post_init(self, __context):
        if not self.DATABASE_URL:
            object.__setattr__(
                self,
                "DATABASE_URL",
                f"postgresql+psycopg2://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DBNAME}",
            )

    # AI
    GROQ_API_KEY: str

    # Email
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@nutriplan.ai"

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Open Food Facts
    OPEN_FOOD_FACTS_BASE_URL: str = "https://world.openfoodfacts.org"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
