import re

def senha_valida(password: str) -> bool:
    """Verifica se a senha cumpre os requisitos mínimos."""
    return (
        len(password) >= 8
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"[0-9]", password)
        and re.search(r"[!@#$%^&*()_+=\-{}\[\]:;\"'<>,.?/]", password)
    )
