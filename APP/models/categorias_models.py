from APP.core.database import conectar
from APP.core.logger import logger


class Categoria:
    """Cadastro de categorias de produtos."""

    @staticmethod
    def listar():
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, nome, segmento FROM categorias ORDER BY nome ASC")
            return cur.fetchall()

    @staticmethod
    def adicionar(nome, segmento="geral"):
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Nome da categoria é obrigatório.")
        segmento = (segmento or "geral").strip() or "geral"

        with conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO categorias (nome, segmento) VALUES (?, ?)",
                (nome, segmento),
            )
            categoria_id = cur.lastrowid
        logger.info("Categoria criada: %s (segmento=%s)", nome, segmento)
        return categoria_id
