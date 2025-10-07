from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    # --- PREFIX ---
    API_PREFIX: str = '/api'

    # --- GRPC ---
    GRPC_HOST: str = 'localhost'
    GRPC_USER_PORT: int = 50051
    GRPC_CHAT_PORT: int = 50052
    GRPC_MESSAGE_PORT: int = 50053

    #--- JWT ---
    SECRET_KEY: str = 'Secret key'
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_LIFESPAN_MINUTES: int = 15
    JWT_REFRESH_LIFESPAN_DAYS: int = 10

settings = Settings()
