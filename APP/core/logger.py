# APP/core/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler
from APP.core.config import config


# ============================================================
# CONFIGURAÇÃO DO LOGGER CENTRAL
# ============================================================

# Caminho do log vem do config.json
LOG_PATH = config.log_path
LOG_DIR = os.path.dirname(LOG_PATH)
os.makedirs(LOG_DIR, exist_ok=True)


# Configuração básica de logging
logger = logging.getLogger("sistema_logger")
logger.setLevel(logging.DEBUG if config.debug else logging.INFO)


# ------------------------------------------------------------
# FORMATADOR PADRÃO
# ------------------------------------------------------------
formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ------------------------------------------------------------
# HANDLER DE ARQUIVO (com rotação)
# ------------------------------------------------------------
file_handler = RotatingFileHandler(
    LOG_PATH,
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=5,
    encoding="utf-8"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# ------------------------------------------------------------
# HANDLER DE CONSOLE
# ------------------------------------------------------------
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# ------------------------------------------------------------
# CONFIRMAÇÃO
# ------------------------------------------------------------
logger.info("=== Logger inicializado ===")
logger.info(f"Arquivo de log: {LOG_PATH}")
