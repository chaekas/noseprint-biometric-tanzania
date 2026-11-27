from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://noseprint:noseprint_dev_password@localhost:5433/noseprint"
    storage_dir: Path = Path("storage")
    model_name: str = "resnet18_imagenet1k_v1"
    model_version: str = "resnet18-imagenet1k-v1"
    embedding_dim: int = 512
    match_threshold: float = 0.75
    max_image_mb: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
