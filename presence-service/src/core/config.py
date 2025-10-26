from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # --- POSTGRES ---
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    @property
    def POSTGRES_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # --- REDIS ---
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    # --- GRPC ---
    GRPC_HOST: str = 'localhost'
    GRPC_PORT: int = 50054

    # --- KAFKA ---
    KAFKA_HOST: str = 'localhost'
    KAFKA_PORT: int = 9092

settings = Settings()
