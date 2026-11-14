"""Application settings loaded from environment variables and an optional .env file."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CLOUDFORGE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "CloudForge"
    version: str = "0.1.0"

    dry_run: bool = True
    max_resources: int = 10
    api_key: str | None = None

    terraform_binary: str = "terraform"
    terraform_timeout_seconds: int = 300
    terraform_module_dir: Path | None = None
    workdir: Path = Path(".cloudforge/workdirs")
