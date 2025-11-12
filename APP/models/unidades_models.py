from APP.core.database import conectar
from APP.core.logger import logger


class UnidadeMedida:
    """Cadastro de unidades de medida reutilizáveis entre segmentos."""

    @staticmethod
    def listar():
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, sigla, descricao FROM unidades_medida ORDER BY sigla ASC")
            return cur.fetchall()

    @staticmethod
    def adicionar(sigla, descricao=None):
        sigla = (sigla or "").strip().upper()
        if not sigla:
            raise ValueError("Sigla da unidade é obrigatória.")
        descricao = (descricao or "").strip() or sigla

        with conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO unidades_medida (sigla, descricao) VALUES (?, ?)",
                (sigla, descricao),
            )
            unidade_id = cur.lastrowid
        logger.info("Unidade cadastrada: %s (%s)", sigla, descricao)
        return unidade_id
