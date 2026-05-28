from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # --- MONGO ---
    MONGO_USER: str
    MONGO_PASS: str
    MONGO_HOST: str
    MONGO_PORT: int

    @property
    def MONGO_URL(self):
        return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASS}@{self.MONGO_HOST}:{self.MONGO_PORT}"

    # --- REDIS ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    # --- GRPC ---
    GRPC_HOST: str = "localhost"
    GRPC_PORT: int = 50053

    # --- KAFKA ---
    KAFKA_HOST: str = "localhost"
    KAFKA_PORT: int = 9092


settings = Settings()
