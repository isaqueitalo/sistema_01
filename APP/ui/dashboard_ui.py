# APP/ui/dashboard_ui.py
import flet as ft
from APP.ui.produtos_ui import ProdutosUI
from APP.ui.vendas_ui import VendasUI
from APP.ui.usuarios_ui import UsuariosUI
from APP.ui.logs_viewer import LogsViewer
from APP.ui.relatorios_ui import RelatoriosUI
from APP.core.logger import logger


class DashboardUI:
    """Painel principal do sistema."""

    def __init__(self, page: ft.Page, username: str, role: str):
        self.page = page
        self.username = username
        self.role = role
        self.build_ui()
        logger.info(f"Dashboard carregado para {username} ({role}).")

    # ==================================================
    # === CONSTRUÇÃO DA INTERFACE =======================
    # ==================================================
    def build_ui(self):
        self.page.clean()
        self.page.title = "Painel Principal"

        # === Cabeçalho ===
        header = ft.Row(
            [
                ft.Text("🏠 Painel de Controle", size=22, weight=ft.FontWeight.BOLD),
                ft.Text(f"Usuário: {self.username} ({self.role})", size=14),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # === Grelha de botões principais ===
        botoes = [
            self._card("📦 Produtos", "Gerencie o estoque", self.abrir_produtos),
            self._card("💰 Vendas", "Registre e visualize vendas", self.abrir_vendas),
        ]

        # Botões exclusivos de administradores
        if self.role == "admin":
            botoes.append(self._card("📊 Relatórios", "Análises e gráficos", self.abrir_relatorios))
            botoes.append(self._card("👥 Usuários", "Gerencie contas do sistema", self.abrir_usuarios))
            botoes.append(self._card("🧾 Logs", "Visualize atividades do sistema", self.abrir_logs))

        # === Layout dos botões ===
        grid = ft.Row(
            controls=botoes,
            alignment=ft.MainAxisAlignment.CENTER,
            wrap=True,
        )

        # === Botão de sair ===
        btn_sair = ft.ElevatedButton(
            "🚪 Sair",
            bgcolor=ft.Colors.ERROR_CONTAINER,
            color=ft.Colors.ON_ERROR_CONTAINER,
            on_click=lambda e: self.voltar_login(),
        )

        self.page.add(
            ft.Column(
                [
                    header,
                    ft.Divider(),
                    grid,
                    ft.Divider(),
                    btn_sair,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            )
        )

    # ==================================================
    # === FUNÇÕES AUXILIARES ============================
    # ==================================================
    def _card(self, titulo, subtitulo, callback):
        """Cria um card de botão."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(titulo, size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(subtitulo, size=13),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=180,
            height=130,
            bgcolor=ft.Colors.PRIMARY_CONTAINER,  # ✅ corrigido
            border_radius=12,
            alignment=ft.alignment.center,
            ink=True,
            on_click=lambda e: callback(),
            padding=10,
        )

    # ==================================================
    # === FUNÇÕES DE NAVEGAÇÃO =========================
    # ==================================================
    def abrir_produtos(self):
        ProdutosUI(self.page, voltar_callback=self.voltar_dashboard)
        logger.info(f"{self.username} abriu o módulo de produtos.")

    def abrir_vendas(self):
        VendasUI(self.page, voltar_callback=self.voltar_dashboard)
        logger.info(f"{self.username} abriu o módulo de vendas.")

    def abrir_usuarios(self):
        if self.role != "admin":
            self.permissao_negada()
            return
        UsuariosUI(self.page, usuario_logado=self.username, voltar_callback=self.voltar_dashboard)
        logger.info(f"{self.username} abriu o módulo de usuários.")

    def abrir_logs(self):
        if self.role != "admin":
            self.permissao_negada()
            return
        LogsViewer(self.page, voltar_callback=self.voltar_dashboard)
        logger.info(f"{self.username} abriu o módulo de logs.")

    def abrir_relatorios(self):
        if self.role != "admin":
            self.permissao_negada()
            return
        RelatoriosUI(self.page, voltar_callback=self.voltar_dashboard)
        logger.info(f"{self.username} abriu o módulo de relatórios.")

    def voltar_dashboard(self):
        """Recarrega o painel principal."""
        self.build_ui()

    def voltar_login(self):
        """Retorna para a tela de login."""
        from APP.ui.login_ui import LoginUI
        self.page.clean()
        LoginUI(self.page)
        logger.info(f"{self.username} saiu do sistema.")

    def permissao_negada(self):
        """Exibe alerta de acesso restrito."""
        dlg = ft.AlertDialog(
            title=ft.Text("Acesso negado ❌"),
            content=ft.Text("Você não possui permissão para acessar esta área."),
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
