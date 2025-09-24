from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env')

    # --- GRPC ---
    GRPC_HOST: str = 'localhost'
    GRPC_PORT: int = 50052

settings = Settings()
