from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    # --- PREFIX ---
    API_PREFIX: str = '/api'

    # --- GRPC ---
    GRPC_HOST: str = 'localhost'
    GRPC_USER_PORT: int = 50051
    GRPC_CHAT_PORT: int = 50052

settings = Settings()
