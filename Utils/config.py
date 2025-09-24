import json
import os
from typing import Any, Dict, Optional

#  Config keys and their default values if there is no config set otherwise
_DEFAULTS: Dict[str, Any] = {
    "appearance_mode": "light",          # "light" | "dark" | "system"
    "prefill_date_on_new": True,         # prefill "Datum" with today for new customers
    "db_path": "data/customers.db",      # fallback; can be overridden
    "supported_languages": ["de"],       # languages for UI and PDF generation
    "support_website": "https://github.com/sweetfamine/sweetNote/issues", # support website
    "app_version": "0.1.0",               # current app version
    "build_date": "24.09.2025",           # build date
    "support_phone": "",                  # support phone number (optional)
    "support_email": "sweet.famine@outlook.de"  # support email (optional)
}

class Config:
    """Minimal JSON-backed config with defaults."""
    def __init__(self, path: Optional[str] = None):
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