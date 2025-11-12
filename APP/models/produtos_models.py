from APP.core.database import conectar
from APP.core.logger import logger


class Produto:
    """Modelo de Produtos com suporte a categorias e unidades."""

    @staticmethod
    def adicionar(
        nome,
        preco,
        estoque,
        fornecedor=None,
        validade=None,
        categoria_id=None,
        unidade_id=None,
        codigo_barras=None,
        estoque_minimo=0,
        localizacao=None,
    ):
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO produtos (
                    nome,
                    preco,
                    estoque,
                    fornecedor,
                    validade,
                    categoria_id,
                    unidade_id,
                    codigo_barras,
                    estoque_minimo,
                    localizacao
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    nome,
                    preco,
                    estoque,
                    fornecedor,
                    validade,
                    categoria_id,
                    unidade_id,
                    codigo_barras,
                    estoque_minimo,
                    localizacao,
                ),
            )
        logger.info(
            "Produto adicionado: %s - R$%.2f (estoque=%s, categoria=%s, unidade=%s)",
            nome,
            preco,
            estoque,
            categoria_id,
            unidade_id,
        )

    @staticmethod
    def listar():
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT
                    p.id,
                    p.nome,
                    p.preco,
                    p.estoque,
                    p.fornecedor,
                    p.validade,
                    c.nome AS categoria_nome,
                    u.sigla AS unidade_sigla,
                    p.codigo_barras,
                    p.estoque_minimo,
                    p.localizacao,
                    p.categoria_id,
                    p.unidade_id
                FROM produtos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                LEFT JOIN unidades_medida u ON p.unidade_id = u.id
                ORDER BY p.nome ASC
                """
            )
            produtos = cur.fetchall()
        return produtos

    @staticmethod
    def atualizar(nome, **dados):
        if not dados:
            raise Exception("Nenhum valor informado para atualizar.")

        campos = []
        valores = []
        colunas_validas = {
            "preco",
            "estoque",
            "fornecedor",
            "validade",
            "categoria_id",
            "unidade_id",
            "codigo_barras",
            "estoque_minimo",
            "localizacao",
        }

        for coluna, valor in dados.items():
            if coluna not in colunas_validas:
                continue
            campos.append(f"{coluna} = ?")
            valores.append(valor)

        if not campos:
            raise Exception("Nenhum valor válido informado para atualizar.")

        valores.append(nome)

        with conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                f"UPDATE produtos SET {', '.join(campos)} WHERE nome = ?",
                valores,
            )
            if cur.rowcount == 0:
                raise Exception(f"Produto '{nome}' não encontrado para atualização.")
        logger.info("Produto '%s' atualizado.", nome)

    @staticmethod
    def excluir(nome):
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM produtos WHERE nome = ?", (nome,))
            if cur.rowcount == 0:
                raise Exception(f"Produto '{nome}' não encontrado para exclusão.")
        logger.info("Produto '%s' excluído.", nome)

    @staticmethod
    def obter_preco(nome_produto):
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute("SELECT preco FROM produtos WHERE nome = ?", (nome_produto,))
            row = cur.fetchone()
        if row:
            return float(row[0])
        raise Exception(f"Produto '{nome_produto}' não encontrado.")

    @staticmethod
    def buscar_por_codigo_ou_nome(valor: str):
        """Retorna o primeiro produto cujo código de barras bate exatamente ou nome contém o termo."""
        valor = (valor or "").strip()
        if not valor:
            return None
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT
                    p.id,
                    p.nome,
                    p.preco,
                    p.estoque,
                    p.codigo_barras
                FROM produtos p
                WHERE LOWER(p.nome) LIKE ?
                   OR (p.codigo_barras IS NOT NULL AND p.codigo_barras = ?)
                ORDER BY CASE WHEN p.codigo_barras = ? THEN 0 ELSE 1 END, p.nome
                LIMIT 1
                """,
                (f"%{valor.lower()}%", valor, valor),
            )
            row = cur.fetchone()
        return row

    @staticmethod
    def buscar_sugestoes(valor: str, limit: int = 5):
        termo = (valor or "").strip().lower()
        if not termo:
            return []
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, nome, preco, estoque, codigo_barras
                FROM produtos
                WHERE LOWER(nome) LIKE ?
                   OR (codigo_barras IS NOT NULL AND codigo_barras LIKE ?)
                ORDER BY nome ASC
                LIMIT ?
                """,
                (f"%{termo}%", f"%{termo}%", limit),
            )
            return cur.fetchall()
