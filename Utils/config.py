import json
import os
import sys
from typing import Any, Dict, Optional

_DEFAULTS: Dict[str, Any] = {
    "appearance_mode": "light",          
    "prefill_date_on_new": True,         
    "db_path": "data/customers.db",      
    "supported_languages": ["de"],       
    "support_website": "https://github.com/sweetfamine/sweetNote/issues",
    "app_version": "0.1.0",
    "build_date": "24.09.2025",
    "support_phone": "",
    "support_email": "sweet.famine@outlook.de"
}

class Config:
    def __init__(self, path: Optional[str] = None):
        if getattr(sys, "frozen", False):
            # Im Build: EXE-Verzeichnis
            root = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # Im Dev: Projekt-Root
            root = os.path.dirname(os.path.dirname(__file__))

        self.path: str = path or os.path.join(root, "config.json")
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}

        for k, v in _DEFAULTS.items():
            self.data.setdefault(k, v)

    def save(self) -> None:
        folder = os.path.dirname(self.path)
        os.makedirs(folder, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, _DEFAULTS.get(key, default))

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    @property
    def file_path(self) -> str:
        return self.path