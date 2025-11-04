# APP/controllers/produtos_controller.py
from typing import List, Tuple, Optional
from APP.models.produtos_models import ProdutoModel
from APP.models.usuarios_models import Log  # registrar ações
# NOTE: não importamos User aqui — o controle de permissão vem do 'role' passado pela UI

class ProdutoController:
    """Controller do módulo Produtos — valida dados e chama o model."""

    @staticmethod
    def ensure_table():
        """Garante que a tabela exista (chamar ao iniciar módulo)."""
        ProdutoModel.criar_tabela()

    # === LISTAGENS / BUSCAS ===
    @staticmethod
    def listar_produtos() -> List[tuple]:
        """Retorna lista de produtos (id, nome, categoria, preco_venda, estoque, data_cadastro)."""
        return ProdutoModel.listar_todos()

    @staticmethod
    def buscar_por_nome(term: str) -> List[tuple]:
        """Busca produtos cujo nome contenha 'term' (case-insensitive)."""
        if term is None:
            term = ""
        return ProdutoModel.buscar_por_nome(term)

    @staticmethod
    def obter_produto(id_produto: int) -> Optional[tuple]:
        """Retorna os dados completos de um produto por ID (ou None)."""
        return ProdutoModel.obter_por_id(id_produto)

    # === CRIAR / ATUALIZAR / EXCLUIR ===
    @staticmethod
    def criar_produto(
        nome: str,
        descricao: str,
        preco_custo: float,
        preco_venda: float,
        estoque: int,
        categoria: str,
        executor: str,
        role: str,
    ) -> Tuple[bool, str]:
        """
        Cria um produto. Apenas 'admin' e 'estoquista' podem criar.
        Retorna (ok, mensagem).
        """
        # Permissão
        if role not in ("admin", "estoquista"):
            return False, "Permissão negada: apenas admin ou estoquista podem criar produtos."

        # Validações básicas
        if not nome or not nome.strip():
            return False, "Nome do produto é obrigatório."
        try:
            preco_custo = float(preco_custo)
            preco_venda = float(preco_venda)
            estoque = int(estoque)
        except Exception:
            return False, "Preço e estoque devem ser numéricos."

        if preco_custo < 0 or preco_venda < 0:
            return False, "Preços não podem ser negativos."
        if estoque < 0:
            return False, "Estoque não pode ser negativo."

        # Inserção
        ProdutoModel.inserir(nome.strip(), descricao or "", preco_custo, preco_venda, estoque, categoria or "")
        Log.registrar(executor, f"produto_criado: {nome.strip()}")
        return True, "Produto criado com sucesso."

    @staticmethod
    def atualizar_produto(
        id_produto: int,
        nome: str,
        descricao: str,
        preco_custo: float,
        preco_venda: float,
        estoque: int,
        categoria: str,
        executor: str,
        role: str,
    ) -> Tuple[bool, str]:
        """
        Atualiza um produto. Apenas 'admin' e 'estoquista' podem atualizar.
        """
        if role not in ("admin", "estoquista"):
            return False, "Permissão negada: apenas admin ou estoquista podem atualizar produtos."

        # Validar existencia
        existing = ProdutoModel.obter_por_id(id_produto)
        if not existing:
            return False, "Produto não encontrado."

        # Validações
        if not nome or not nome.strip():
            return False, "Nome do produto é obrigatório."

        try:
            preco_custo = float(preco_custo)
            preco_venda = float(preco_venda)
            estoque = int(estoque)
        except Exception:
            return False, "Preço e estoque devem ser numéricos."

        if preco_custo < 0 or preco_venda < 0:
            return False, "Preços não podem ser negativos."
        if estoque < 0:
            return False, "Estoque não pode ser negativo."

        ProdutoModel.atualizar(id_produto, nome.strip(), descricao or "", preco_custo, preco_venda, estoque, categoria or "")
        Log.registrar(executor, f"produto_atualizado: id={id_produto} nome={nome.strip()}")
        return True, "Produto atualizado com sucesso."

    @staticmethod
    def excluir_produto(id_produto: int, executor: str, role: str) -> Tuple[bool, str]:
        """
        Exclui um produto. Apenas 'admin' pode excluir (política definida).
        """
        if role != "admin":
            return False, "Permissão negada: apenas admin pode excluir produtos."

        existing = ProdutoModel.obter_por_id(id_produto)
        if not existing:
            return False, "Produto não encontrado."

        ProdutoModel.excluir(id_produto)
        Log.registrar(executor, f"produto_excluido: id={id_produto}")
        return True, "Produto excluído com sucesso."
