import hashlib


def hash_password(password: str) -> str:
    """Gera hash SHA256 da senha."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verificar_senha(password: str, senha_hash: str) -> bool:
    """Compara senha com hash armazenado."""
    return hash_password(password) == senha_hash
