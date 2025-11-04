# APP/models/produtos_model.py
import sqlite3
from datetime import datetime
from APP.database import conectar


class ProdutoModel:
    """Model responsável pelas operações no banco de produtos."""

    @staticmethod
    def criar_tabela():
        """Cria a tabela 'produtos' se não existir."""
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                preco_custo REAL NOT NULL DEFAULT 0.0,
                preco_venda REAL NOT NULL DEFAULT 0.0,
                estoque INTEGER NOT NULL DEFAULT 0,
                categoria TEXT,
                data_cadastro TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    # =====================================================
    # === CRUD BÁSICO (Create, Read, Update, Delete) ===
    # =====================================================

    @staticmethod
    def inserir(nome, descricao, preco_custo, preco_venda, estoque, categoria):
        """Insere um novo produto no banco."""
        conn = conectar()
        cursor = conn.cursor()
        data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO produtos (nome, descricao, preco_custo, preco_venda, estoque, categoria, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nome, descricao, preco_custo, preco_venda, estoque, categoria, data_cadastro))
        conn.commit()
        conn.close()

    @staticmethod
    def listar_todos():
        """Retorna todos os produtos cadastrados."""
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, categoria, preco_venda, estoque, data_cadastro
            FROM produtos
            ORDER BY id ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def obter_por_id(id_produto):
        """Retorna um produto pelo ID."""
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, descricao, preco_custo, preco_venda, estoque, categoria, data_cadastro
            FROM produtos
            WHERE id = ?
        """, (id_produto,))
        produto = cursor.fetchone()
        conn.close()
        return produto

    @staticmethod
    def buscar_por_nome(termo):
        """Busca produtos pelo nome (parcial, case-insensitive)."""
        conn = conectar()
        cursor = conn.cursor()
        termo_busca = f"%{termo}%"
        cursor.execute("""
            SELECT id, nome, categoria, preco_venda, estoque, data_cadastro
            FROM produtos
            WHERE nome LIKE ?
            ORDER BY nome ASC
        """, (termo_busca,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def atualizar(id_produto, nome, descricao, preco_custo, preco_venda, estoque, categoria):
        """Atualiza os dados de um produto existente."""
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE produtos
            SET nome = ?, descricao = ?, preco_custo = ?, preco_venda = ?, estoque = ?, categoria = ?
            WHERE id = ?
        """, (nome, descricao, preco_custo, preco_venda, estoque, categoria, id_produto))
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(id_produto):
        """Remove um produto do banco."""
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
        conn.commit()
        conn.close()
