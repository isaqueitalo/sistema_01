import logging
from APP.core.config import LOG_FILE

logger = logging.getLogger("sistema_logger")
logger.setLevel(logging.INFO)

fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info("=== Logger inicializado ===")
logger.info(f"Arquivo de log: {LOG_FILE}")
