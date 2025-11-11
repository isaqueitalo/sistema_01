from APP.core.database import conectar
from APP.core.logger import logger


class Venda:
    """Modelo de Vendas"""

    @staticmethod
    def registrar(produto, quantidade, total, vendedor=None):
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO vendas (produto, quantidade, total, vendedor, data_hora)
                VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
                """,
                (produto, quantidade, total, vendedor),
            )
        logger.info(
            f"Venda registrada: {produto} x{quantidade} = R$ {total:.2f} por {vendedor if vendedor else 'desconhecido'}"
        )


    @staticmethod
    def listar():
         with conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, produto, quantidade, total, vendedor, data_hora FROM vendas ORDER BY id DESC"
            )
            rows = cur.fetchall()
            return rows

    @staticmethod
    def listar_periodo(data_inicio, data_fim):
        """Retorna todas as vendas entre as datas informadas (inclusive)."""
        try:
            with conectar() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT id, produto, quantidade, total, vendedor, data_hora
                    FROM vendas
                    WHERE substr(data_hora, 1, 10) BETWEEN ? AND ?
                    ORDER BY data_hora ASC
                    """,
                    (data_inicio, data_fim),
                )
                rows = cur.fetchall()

            logger.info(f"{len(rows)} vendas encontradas no período {data_inicio} → {data_fim}")
            return rows

        except Exception as e:
            logger.error(f"Erro ao buscar vendas no período: {e}", exc_info=True)
            return []
