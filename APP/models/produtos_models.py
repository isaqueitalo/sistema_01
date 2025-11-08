# APP/models/produtos_models.py
from APP.core.database import conectar
from APP.core.logger import logger


class Produto:
    """Modelo de Produtos"""

    @staticmethod
    def adicionar(nome, preco, estoque):
        conn = conectar()
        cur = conn.cursor()
        cur.execute("INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)", (nome, preco, estoque))
        conn.commit()
        conn.close()
        logger.info(f"Produto adicionado: {nome} - R${preco:.2f}, estoque={estoque}")

    @staticmethod
    def listar():
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, preco, estoque FROM produtos ORDER BY nome ASC")
        produtos = cur.fetchall()
        conn.close()
        return produtos

    @staticmethod
    def atualizar(nome, preco=None, estoque=None):
        conn = conectar()
        cur = conn.cursor()

        campos = []
        valores = []

        if preco is not None:
            campos.append("preco = ?")
            valores.append(preco)

        if estoque is not None:
            campos.append("estoque = ?")
            valores.append(estoque)

        if not campos:
            raise Exception("Nenhum valor informado para atualizar.")

        valores.append(nome)
        cur.execute(f"UPDATE produtos SET {', '.join(campos)} WHERE nome = ?", valores)
        conn.commit()
        conn.close()
        logger.info(f"Produto '{nome}' atualizado com sucesso.")

    @staticmethod
    def excluir(nome):
        conn = conectar()
        cur = conn.cursor()
        cur.execute("DELETE FROM produtos WHERE nome = ?", (nome,))
        conn.commit()
        conn.close()
        logger.info(f"Produto '{nome}' excluído.")

    @staticmethod
    def obter_preco(nome_produto):
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT preco FROM produtos WHERE nome = ?", (nome_produto,))
        row = cur.fetchone()
        conn.close()
        if row:
            return float(row[0])
        else:
            raise Exception(f"Produto '{nome_produto}' não encontrado.")
