from APP.core.database import conectar
from APP.core.logger import logger
import sqlite3

class Produto:
    """Modelo de Produtos (com fornecedor e validade)."""

    @staticmethod
    def adicionar(nome, preco, estoque, fornecedor=None, validade=None):
        conn = conectar()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO produtos (nome, preco, estoque, fornecedor, validade)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, preco, estoque, fornecedor, validade))
            conn.commit()
            logger.info(
                f"Produto adicionado: {nome} - R${preco:.2f}, estoque={estoque}, "
                f"fornecedor={fornecedor}, validade={validade}"
            )
        except sqlite3.IntegrityError as ie:
            # Nome já existe (UNIQUE)
            logger.warning(f"Tentativa de inserir produto duplicado: {nome}")
            raise ValueError(f"Já existe um produto chamado '{nome}'.") from ie
        finally:
            conn.close()

    @staticmethod
    def listar():
        """Retorna (id, nome, preco, estoque, fornecedor, validade)"""
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nome, preco, estoque, fornecedor, validade
            FROM produtos
            ORDER BY nome ASC
        """)
        rows = cur.fetchall()
        conn.close()
        # Normaliza para tupla simples (evita depender de sqlite3.Row)
        return [(
            r[0],              # id
            r[1],              # nome
            float(r[2]),       # preco
            int(r[3]),         # estoque
            (r[4] or None),    # fornecedor
            (r[5] or None),    # validade (YYYY-MM-DD ou None)
        ) for r in rows]

    @staticmethod
    def atualizar(nome, preco=None, estoque=None, fornecedor=None, validade=None):
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

        # Campos textuais opcionais: permitir limpar com None
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
