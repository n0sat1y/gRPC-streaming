from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    # --- PREFIX ---
    API_PREFIX: str = '/api'

settings = Settings()
