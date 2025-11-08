# APP/core/config_manager.py
import json
import os

CONFIG_PATH = os.path.join("DATA", "config.json")


def carregar_config():
    """Carrega as configurações do sistema."""
    if not os.path.exists(CONFIG_PATH):
        return {"tema": "dark"}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"tema": "dark"}


def salvar_config(config):
    """Salva as configurações."""
    os.makedirs("DATA", exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
