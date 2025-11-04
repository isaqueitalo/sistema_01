# APP/utils.py
import re
import hashlib  # <-- Adicione este import

def senha_valida(password: str) -> bool:
    """Verifica se a senha cumpre os requisitos mínimos."""
    return (
        len(password) >= 8
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"[0-9]", password)
        and re.search(r"[!@#$%^&*()_+=\-{}\[\]:;\"'<>,.?/]", password)
    )


def hash_password(password: str) -> str:
    """Gera um hash SHA256 para a senha."""
    return hashlib.sha256(password.encode()).hexdigest()