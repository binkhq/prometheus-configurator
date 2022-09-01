from pydantic import BaseSettings, DirectoryPath
from pathlib import Path


class Settings(BaseSettings):
    source_directory: DirectoryPath
    destination_file: Path


settings = Settings()
