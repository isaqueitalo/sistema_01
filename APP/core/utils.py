import hashlib
import os


def hash_password(password: str) -> str:
    """
    Gera um hash SHA-256 seguro para a senha com salt fixo.
    ⚠️ Em um ambiente real, o salt deve ser único por usuário.
    """
    salt = "SISTEMA_GESTAO@2025"
    return hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()


def check_password(password: str, stored_hash: str) -> bool:
    """
    Verifica se a senha informada corresponde ao hash armazenado.
    """
    return hash_password(password) == stored_hash


def gerar_chave_unica() -> str:
    """
    Gera uma chave única (UUID-like) para uso em tokens, códigos de redefinição, etc.
    """
    return hashlib.sha256(os.urandom(32)).hexdigest()
