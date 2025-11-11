from APP.core.database import conectar
from APP.core.logger import logger
import sqlite3

class Produto:
    """Modelo de Produtos (com fornecedor e validade)."""

    @staticmethod
    def adicionar(nome, preco, estoque, fornecedor=None, validade=None):
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO produtos (nome, preco, estoque, fornecedor, validade)
                VALUES (?, ?, ?, ?, ?)
                """,
                (nome, preco, estoque, fornecedor, validade),
            )
        logger.info(
            f"Produto adicionado: {nome} - R${preco:.2f}, estoque={estoque}, fornecedor={fornecedor}, validade={validade}"
        )

    @staticmethod
    def listar():
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, nome, preco, estoque, fornecedor, validade FROM produtos ORDER BY nome ASC"
            )
            produtos = cur.fetchall()
        return produtos

    @staticmethod
    def atualizar(nome, preco=None, estoque=None, fornecedor=None, validade=None):
        campos = []
        valores = []

        if preco is not None:
            campos.append("preco = ?")
            valores.append(preco)

        if estoque is not None:
            campos.append("estoque = ?")
            valores.append(estoque)

        if fornecedor is not None:
            campos.append("fornecedor = ?")
            valores.append(fornecedor)

        if validade is not None:
            campos.append("validade = ?")
            valores.append(validade)

        if not campos:
            conn.close()
            raise Exception("Nenhum valor informado para atualizar.")

        valores.append(nome)

        with conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                f"UPDATE produtos SET {', '.join(campos)} WHERE nome = ?",
                valores,
            )
        logger.info(f"Produto '{nome}' atualizado com sucesso.")

    @staticmethod
    def excluir(nome):
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM produtos WHERE nome = ?", (nome,))
        logger.info(f"Produto '{nome}' excluído.")

    @staticmethod
    def obter_preco(nome_produto):
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute("SELECT preco FROM produtos WHERE nome = ?", (nome_produto,))
            row = cur.fetchone()
        if row:
            return float(row[0])
        else:
            raise Exception(f"Produto '{nome_produto}' não encontrado.")
