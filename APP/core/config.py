# APP/core/config.py
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "config.json")
CONFIG_PATH = os.path.abspath(CONFIG_PATH)


class Config:
    """Carrega e gerencia as configurações do sistema a partir do config.json"""

    def __init__(self):
        self.data = self._load_config()

    def _load_config(self):
        if not os.path.exists(CONFIG_PATH):
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {CONFIG_PATH}")
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def get(self, key, default=None):
        """Retorna um valor de configuração"""
        return self.data.get(key, default)

    @property
    def app_name(self):
        return self.data.get("app_name", "Sistema")

    @property
    def db_path(self):
        return os.path.abspath(self.data.get("database_path", "DATA/system.db"))

    @property
    def log_path(self):
        return os.path.abspath(self.data.get("log_path", "DATA/system.log"))

    @property
    def default_users(self):
        return self.data.get("default_users", [])

    @property
    def theme(self):
        return self.data.get("theme", "dark")

    @property
    def debug(self):
        return bool(self.data.get("debug", False))


# Instância global reutilizável
config = Config()
