# APP/core/session.py
"""
Gerenciador simples de sessões em memória.

Funcionalidades:
- start_session(username, role) -> session_id (UUID string)
- end_session(session_id)
- get_session(session_id)
- touch(session_id) -> atualiza last_active
- get_active_sessions() -> lista de sessões não expiradas
- cleanup_expired(timeout_seconds) -> remove sessões inativas
- decorator require_role(min_role) -> verifica role em handlers (ex.: Flet callbacks)

Observação: é um gerenciador em memória — se precisar persistir sessões entre restarts,
implemente armazenamento no DB ou Redis.
"""

import uuid
import time
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from APP.core.logger import logger
from threading import Lock
import functools


@dataclass
class Session:
    session_id: str
    username: str
    role: str
    started_at: float
    last_active: float


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._lock = Lock()

    def start_session(self, username: str, role: str) -> str:
        """Cria nova sessão e retorna session_id."""
        sid = str(uuid.uuid4())
        now = time.time()
        s = Session(session_id=sid, username=username, role=role, started_at=now, last_active=now)
        with self._lock:
            self._sessions[sid] = s
        logger.info(f"Session started: {username} ({role}) -> {sid}")
        return sid

    def end_session(self, session_id: str) -> bool:
        """Encerra sessão. Retorna True se removida, False se não encontrada."""
        with self._lock:
            if session_id in self._sessions:
                s = self._sessions.pop(session_id)
                logger.info(f"Session ended: {s.username} ({s.role}) -> {session_id}")
                return True
        logger.debug(f"Tentativa de encerrar sessão inexistente: {session_id}")
        return False

    def get_session(self, session_id: str) -> Optional[Session]:
        with self._lock:
            return self._sessions.get(session_id)

    def touch(self, session_id: str):
        """Atualiza last_active para agora."""
        with self._lock:
            s = self._sessions.get(session_id)
            if s:
                s.last_active = time.time()
                logger.debug(f"Session touch: {s.username} -> {session_id}")

    def get_active_sessions(self) -> Dict[str, Dict]:
        """Retorna dicionário simples de sessões ativas."""
        with self._lock:
            return {sid: asdict(s) for sid, s in self._sessions.items()}

    def cleanup_expired(self, timeout_seconds: int = 3600) -> int:
        """
        Remove sessões inativas por mais de timeout_seconds.
        Retorna o número de sessões removidas.
        """
        now = time.time()
        removed = 0
        with self._lock:
            to_remove = [sid for sid, s in self._sessions.items() if now - s.last_active > timeout_seconds]
            for sid in to_remove:
                s = self._sessions.pop(sid)
                removed += 1
                logger.info(f"Session expired and removed: {s.username} -> {sid}")
        return removed


# Instância global (padrão único dentro do processo)
session_manager = SessionManager()


# --------------------------
# Decorator simples de permissão
# --------------------------
ROLE_HIERARCHY = {
    "admin_master": 3,
    "admin": 2,
    "vendedor": 1,
    "user": 0,
}


def require_role(min_role: str):
    """
    Decorator que valida se a sessão (passada como primeiro argumento) pertence a um usuário
    com role >= min_role na hierarquia ROLE_HIERARCHY.

    Uso (exemplo):
        @require_role("admin")
        def handler(session_id, *args, **kwargs):
            # aqui session_id é garantido válido e com role suficiente
            ...

    Observação: o handler deve receber session_id como primeiro argumento.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(session_id, *args, **kwargs):
            s = session_manager.get_session(session_id)
            if not s:
                logger.warning("Ação bloqueada: sessão inválida.")
                raise PermissionError("Sessão inválida ou expirada.")
            role_value = ROLE_HIERARCHY.get(s.role, 0)
            min_value = ROLE_HIERARCHY.get(min_role, 0)
            if role_value < min_value:
                logger.warning(f"Ação bloqueada: usuário '{s.username}' role '{s.role}' insuficiente (requer: {min_role}).")
                raise PermissionError("Permissão negada.")
            # atualiza atividade
            session_manager.touch(session_id)
            return func(session_id, *args, **kwargs)
        return wrapper
    return decorator
