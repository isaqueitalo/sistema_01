from APP.core.database import conectar
from APP.core.logger import logger


class Venda:
    """Modelo de Vendas"""

    @staticmethod
    def registrar(produto, quantidade, total):
        conn = conectar()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO vendas (produto, quantidade, total, data_hora) VALUES (?, ?, ?, datetime('now', 'localtime'))",
            (produto, quantidade, total),
        )
        conn.commit()
        conn.close()
        logger.info(f"Venda registrada: {produto} x{quantidade} = R$ {total:.2f}")

    @staticmethod
    def listar():
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT id, produto, quantidade, total, data_hora FROM vendas ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def listar_periodo(data_inicio, data_fim):
        """Retorna todas as vendas entre as datas informadas (inclusive)."""
        try:
            conn = conectar()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, produto, quantidade, total, data_hora 
                FROM vendas
                WHERE substr(data_hora, 1, 10) BETWEEN ? AND ?
                ORDER BY data_hora ASC
                """,
                (data_inicio, data_fim),
            )
            rows = cur.fetchall()
            conn.close()

            logger.info(f"{len(rows)} vendas encontradas no período {data_inicio} → {data_fim}")
            return rows

        except Exception as e:
            logger.error(f"Erro ao buscar vendas no período: {e}", exc_info=True)
            return []
