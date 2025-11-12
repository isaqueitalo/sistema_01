import time
import flet as ft
from APP.core.logger import logger
from APP.core.session import session_manager
from APP.ui.vendas_ui import VendasUI
from APP.ui.produtos_ui import ProdutosUI
from APP.ui.usuarios_ui import UsuariosUI
from APP.ui.relatorios_ui import RelatoriosUI
from APP.ui.logs_viewer import LogsViewer
from APP.ui import style


class DashboardUI:
    """Tela principal com atalhos rápidos padronizados no visual do novo PDV."""

    def __init__(self, page: ft.Page, username: str, role: str, session_id: str):
        self.page = page
        self.username = username
        self.role = role
        self.session_id = session_id
        self.page.clean()
        self.page.title = f"Dashboard - {username} ({role})"
        self.page.bgcolor = style.BACKGROUND
        self.build_ui()
        logger.info("Dashboard carregado para %s (%s).", username, role)

    # ============================================================
    # INTERFACE
    # ============================================================
    def build_ui(self):
        header = ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(
                            "Central de Operações",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=style.TEXT_DARK,
                        ),
                        ft.Text(
                            f"Bem-vindo, {self.username}",
                            size=14,
                            color=style.TEXT_MUTED,
                        ),
                    ],
                    spacing=4,
                ),
                ft.Container(expand=True),
                style.danger_button("Sair", icon=ft.Icons.LOGOUT, on_click=self.logout),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        cards = [
            self._card("📦 Produtos", "Cadastro, estoque e categorias", self.abrir_produtos),
            self._card("🛒 PDV", "Registrar vendas com atalhos", self.abrir_vendas),
            self._card("📑 Relatórios", "PDF, gráficos e indicadores", self.abrir_relatorios),
        ]

        if self.role in ("admin", "admin_master"):
            cards.append(self._card("👥 Usuários", "Permissões e contas", self.abrir_usuarios))

        if self.role == "admin_master":
            cards.append(self._card("🪵 Logs", "Auditoria e ocorrências", self.abrir_logs))

        sessoes_section = []
        if self.role in ("admin", "admin_master"):
            sessoes_section = [
                ft.Divider(color=style.DIVIDER),
                ft.Text(
                    "📡 Sessões ativas",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=style.TEXT_DARK,
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
                    spacing=18,
                    run_spacing=18,
                ),
                *sessoes_section,
            ],
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

    def _card(self, titulo: str, subtitulo: str, callback):
        tile = ft.Container(
            content=ft.Column(
                [
                    ft.Text(titulo, size=16, weight=ft.FontWeight.W_600, color=style.TEXT_DARK),
                    ft.Text(subtitulo, size=12, color=style.TEXT_MUTED, text_align=ft.TextAlign.CENTER),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=style.PANEL_MUTED,
            border_radius=14,
            padding=ft.Padding(20, 24, 20, 24),
            ink=True,
            border=ft.border.all(1, style.BORDER),
            animate=ft.Animation(120, "easeInOut"),
            on_click=lambda _: callback(),
            col={"xs": 12, "sm": 6, "md": 3},
        )

        def on_hover(e):
            tile.bgcolor = style.ACCENT if e.data == "true" else style.PANEL_MUTED
            tile.content.controls[0].color = style.TEXT_PRIMARY if e.data == "true" else style.TEXT_DARK
            tile.content.controls[1].color = style.TEXT_PRIMARY if e.data == "true" else style.TEXT_MUTED
            tile.update()

        tile.on_hover = on_hover
        return tile

    def _exibir_sessoes(self):
        sessoes = session_manager.get_active_sessions()
        if not sessoes:
            return ft.Text("Nenhuma sessão ativa no momento.", color=style.TEXT_MUTED)

        lista = []
        for sid, s in sessoes.items():
            minutos = int((time.time() - s["started_at"]) // 60)
            lista.append(
                ft.Text(
                    f"• {s['username']} ({s['role']}) — ativo há {minutos} min",
                    color=style.TEXT_MUTED,
                )
            )
        return ft.Column(lista, spacing=4)

    # ============================================================
    # AÇÕES
    # ============================================================
    def logout(self, _):
        try:
            session_manager.end_session(self.session_id)
            self._registrar_log("logout")
        except Exception as err:
            logger.error("Erro ao encerrar sessão: %s", err)

        from APP.ui.login_ui import LoginUI

        self.page.clean()
        LoginUI(self.page)

    def abrir_produtos(self):
        ProdutosUI(self.page, self.voltar_dashboard)

    def abrir_vendas(self):
        VendasUI(self.page, self.voltar_dashboard, vendedor=self.username)

    def abrir_usuarios(self):
        UsuariosUI(self.page, self.voltar_dashboard, current_role=self.role, current_user=self.username)

    def abrir_relatorios(self):
        RelatoriosUI(self.page, self.voltar_dashboard)

    def abrir_logs(self):
        LogsViewer(self.page, self.voltar_dashboard)

    def voltar_dashboard(self):
        self.page.clean()
        self.build_ui()

    def _registrar_log(self, acao: str):
        try:
            from APP.core.database import conectar

            conn = conectar()
            cur = conn.cursor()
            cur.execute("INSERT INTO logs (usuario, acao) VALUES (?, ?)", (self.username, acao))
            conn.commit()
            conn.close()
        except Exception as err:
            logger.error("Erro ao registrar log '%s': %s", acao, err, exc_info=True)
