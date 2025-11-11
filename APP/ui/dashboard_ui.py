import flet as ft
from APP.core.logger import logger
from APP.core.session import session_manager
from APP.ui.vendas_ui import VendasUI
from APP.ui.produtos_ui import ProdutosUI
from APP.ui.usuarios_ui import UsuariosUI
from APP.ui.relatorios_ui import RelatoriosUI
from APP.ui import style
import time


class DashboardUI:
    """Tela principal do sistema com controle de sessão e permissões."""

    def __init__(self, page: ft.Page, username: str, role: str, session_id: str):
        self.page = page
        self.username = username
        self.role = role
        self.session_id = session_id
        self.page.clean()
        self.page.title = f"Dashboard - {username} ({role})"
        self.page.bgcolor = style.BACKGROUND
        self.build_ui()
        logger.info(f"Dashboard carregado para {username} ({role}).")

    # ============================================================
    # === INTERFACE PRINCIPAL ===================================
    # ============================================================
    def build_ui(self):
        header = ft.Row(
            [
                ft.Text(
                    f"Bem-vindo, {self.username}!",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=style.TEXT_PRIMARY,
                ),
                ft.Container(expand=True),
                style.danger_button("Sair", icon=ft.Icons.LOGOUT_ROUNDED, on_click=self.logout),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        cards = [
            self._card("📦 Produtos", "Gerencie o estoque", self.abrir_produtos),
            self._card("💰 Vendas", "Controle as vendas e histórico", self.abrir_vendas),
            self._card("📊 Relatórios", "Gere relatórios e PDFs", self.abrir_relatorios),
        ]

        # Só admin e admin_master veem os usuários
        if self.role in ("admin", "admin_master"):
            cards.append(
                self._card("👥 Usuários", "Gerencie contas e permissões", self.abrir_usuarios)
            )

        sessoes_col = []
        if self.role in ("admin", "admin_master"):
            sessoes_col = [
                ft.Divider(color=style.DIVIDER),
                ft.Text(
                    "💻 Sessões Ativas",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=style.TEXT_PRIMARY,
                ),
                self._exibir_sessoes(),
            ]

        content = ft.Column(
            [
                header,
                ft.Divider(color=style.DIVIDER),
                ft.ResponsiveRow(
                    cards,
                    alignment=ft.MainAxisAlignment.CENTER,
                    run_spacing=20,
                    spacing=20,
                ),
                *sessoes_col,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=24,
        )
        self.page.add(
            ft.Container(
                content=style.surface_container(content, padding=32),
                padding=ft.Padding(24, 24, 24, 24),
                expand=True,
                alignment=ft.alignment.center,
            )
        )
        self.page.update()

    # ============================================================
    # === CARDS COMPACTOS =======================================
    # ============================================================
    def _card(self, titulo, subtitulo, callback):
        """Cria um card clicável moderno e responsivo com hover funcional."""
        c = ft.Container(
            content=ft.Column(
                [
                   ft.Text(titulo, size=15, weight=ft.FontWeight.W_600, color=style.TEXT_PRIMARY),
                    ft.Text(subtitulo, size=12, color=style.TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
            
            bgcolor=style.SURFACE_ALT,
            border_radius=12,
            padding=ft.Padding(16, 20, 16, 20),
            ink=True,
            border=ft.border.all(1, style.BORDER),
            animate=ft.Animation(150, "easeInOut"),
            on_click=lambda e: callback(),
            col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
        )

        # Corrigido: agora a animação de hover é feita alterando a propriedade diretamente
        def on_hover(e):
            if e.data == "true":
                c.bgcolor = style.ACCENT
            else:
                c.bgcolor = style.SURFACE_ALT
            c.update()

        c.on_hover = on_hover
        return c

    # ============================================================
    # === LISTAGEM DE SESSÕES ===================================
    # ============================================================
    def _exibir_sessoes(self):
        sessoes = session_manager.get_active_sessions()
        if not sessoes:
            return ft.Text("Nenhuma sessão ativa.", color=style.TEXT_SECONDARY)

        lista = []
        for sid, s in sessoes.items():
            tempo = int(time.time() - s["started_at"])
            minutos = tempo // 60
            lista.append(
                ft.Text(
                    f"• {s['username']} ({s['role']}) — ativo há {minutos} min",
                    color=style.TEXT_SECONDARY,
                )
            )
        return ft.Column(lista, spacing=4)

    # ============================================================
    # === AÇÕES ==================================================
    # ============================================================
    def logout(self, e):
        try:
            session_manager.end_session(self.session_id)
            self._registrar_log("logout")
            logger.info(f"Usuário '{self.username}' fez logout.")
        except Exception as err:
            logger.error(f"Erro ao encerrar sessão: {err}")

        # Import local para evitar circular import
        from APP.ui.login_ui import LoginUI
        self.page.clean()
        LoginUI(self.page)

    def abrir_produtos(self):
        ProdutosUI(self.page, self.voltar_dashboard)

    def abrir_vendas(self):
        VendasUI(self.page, self.voltar_dashboard, vendedor=self.username)

    def abrir_usuarios(self):
        UsuariosUI(self.page, self.voltar_dashboard)

    def abrir_relatorios(self):
        RelatoriosUI(self.page, self.voltar_dashboard)

    def voltar_dashboard(self):
        self.page.clean()
        self.build_ui()

    def _registrar_log(self, acao):
        try:
            from APP.core.database import conectar
            conn = conectar()
            cur = conn.cursor()
            cur.execute("INSERT INTO logs (usuario, acao) VALUES (?, ?)", (self.username, acao))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Erro ao registrar log '{acao}': {e}", exc_info=True)
