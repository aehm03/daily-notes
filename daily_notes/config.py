import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel


class ConfigData(BaseModel):
    google_api_key: Optional[str] = None


class Config:
    def __init__(self, app_dir: Optional[Path] = None):
        self.app_dir = app_dir or Path("~/.config/daily-notes").expanduser()
        self.config_file = self.app_dir / "config.json"
        self.app_dir.mkdir(parents=True, exist_ok=True)
    
    def get_api_key(self) -> Optional[str]:
        if not self.config_file.exists():
            return None
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                config_data = ConfigData(**data)
                return config_data.google_api_key
        except (json.JSONDecodeError, OSError, ValueError):
            return None
    
    def set_api_key(self, api_key: str) -> None:
        config_data = ConfigData(google_api_key=api_key)
        with open(self.config_file, 'w') as f:
            json.dump(config_data.model_dump(), f, indent=2)