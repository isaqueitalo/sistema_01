from APP.core.database import conectar
from APP.core.logger import logger


class Venda:
    """Modelo de Vendas"""

    @staticmethod
    def registrar(produto, quantidade, total, vendedor=None, cliente=None, forma_pagamento=None, pedido_id=None):
        with conectar() as conn:
            cur = conn.cursor()

            # Garante que o produto exista e que haja estoque suficiente
            cur.execute("SELECT estoque, preco FROM produtos WHERE nome = ?", (produto,))
            row = cur.fetchone()

            if row is None:
                raise Exception(f"Produto '{produto}' não encontrado para registrar a venda.")

            estoque_atual, preco_unitario = int(row[0]), float(row[1])

            if quantidade <= 0:
                raise Exception("Quantidade inválida para venda.")

            if estoque_atual < quantidade:
                raise Exception(
                    f"Estoque insuficiente para '{produto}'. Disponível: {estoque_atual}, solicitado: {quantidade}."
                )

            # Atualiza estoque do produto
            novo_estoque = estoque_atual - quantidade
            cur.execute(
                "UPDATE produtos SET estoque = ? WHERE nome = ?",
                (novo_estoque, produto),
            )

            # Registra a venda
            total_calculado = round(preco_unitario * quantidade, 2)
            if total is not None and abs(total - total_calculado) > 0.01:
                logger.warning(
                    "Total informado (R$ %.2f) difere do calculado (R$ %.2f) para '%s'.",
                    total,
                    total_calculado,
                    produto,
                )
            cur.execute(
                """
                INSERT INTO vendas (produto, quantidade, total, vendedor, cliente, forma_pagamento, pedido_id, data_hora)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
                """,
                (produto, quantidade, total_calculado, vendedor, cliente, forma_pagamento, pedido_id),
            )

        logger.info(
            "Venda registrada: pedido=%s | %s x%d = R$ %.2f por %s (estoque restante: %d) | cliente=%s | pagamento=%s",
            pedido_id or "N/D",
            produto,
            quantidade,
            total_calculado,
            vendedor if vendedor else "desconhecido",
            novo_estoque,
            cliente or "Consumidor Final",
            forma_pagamento or "N/D",
        )

    @staticmethod
    def listar():
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, produto, quantidade, total, vendedor, data_hora, cliente, forma_pagamento, pedido_id FROM vendas ORDER BY id DESC"
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
                    SELECT id, produto, quantidade, total, vendedor, data_hora, cliente, forma_pagamento, pedido_id
                    FROM vendas
                    WHERE substr(data_hora, 1, 10) BETWEEN ? AND ?
                    ORDER BY data_hora ASC
                    """,
                    (data_inicio, data_fim),
                )
                rows = cur.fetchall()

            pedidos_map = {}
            pedidos = []
            for row in rows:
                pedido_id = row[8] or f"LEGACY-{row[0]}"
                if pedido_id not in pedidos_map:
                    pedido = {
                        "pedido_id": pedido_id,
                        "data_hora": row[5],
                        "vendedor": row[4] or "N/D",
                        "cliente": row[6] or "Consumidor Final",
                        "forma_pagamento": row[7] or "N/D",
                        "total": 0.0,
                        "itens": [],
                    }
                    pedidos_map[pedido_id] = pedido
                    pedidos.append(pedido)
                pedido = pedidos_map[pedido_id]
                pedido["itens"].append(
                    {
                        "id": row[0],
                        "produto": row[1],
                        "quantidade": row[2],
                        "total": row[3],
                    }
                )
                pedido["total"] += row[3]

            logger.info(f"{len(pedidos)} pedidos encontrados no período {data_inicio} → {data_fim}")
            return pedidos

        except Exception as e:
            logger.error(f"Erro ao buscar vendas no período: {e}", exc_info=True)
            return []
