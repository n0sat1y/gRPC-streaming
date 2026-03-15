from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # --- PREFIX ---
    API_PREFIX: str = "/api"

    # --- GRPC ---
    GRPC_USER_HOST: str = "localhost"
    GRPC_USER_PORT: int = 50051
    GRPC_CHAT_HOST: str = "localhost"
    GRPC_CHAT_PORT: int = 50052
    GRPC_MESSAGE_HOST: str = "localhost"
    GRPC_MESSAGE_PORT: int = 50053
    GRPC_PRESENCE_HOST: str = "localhost"
    GRPC_PRESENCE_PORT: int = 50054

    # --- KAFKA ---
    KAFKA_HOST: str = "localhost"
    KAFKA_PORT: int = 9092

    # --- REDIS ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    # --- JWT ---
    SECRET_KEY: str = "Secret key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_LIFESPAN_MINUTES: int = 150
    JWT_REFRESH_LIFESPAN_DAYS: int = 10


settings = Settings()
