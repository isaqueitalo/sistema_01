import flet as ft
from APP.core.config_manager import carregar_config
from APP.models.usuarios_models import User
from APP.ui.dashboard_ui import DashboardUI
from APP.core.logger import logger



# APP/ui/login_ui.py
import flet as ft
from APP.core.config_manager import carregar_config
from APP.models.usuarios_models import User
from APP.ui.dashboard_ui import DashboardUI
from APP.core.logger import logger


class LoginUI:
    """Tela minimalista de login com suporte a tema escuro/claro."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.config = carregar_config()
        self.page.theme_mode = ft.ThemeMode.DARK if self.config["tema"] == "dark" else ft.ThemeMode.LIGHT
        self.build_ui()
        logger.info("Tela de login carregada com suporte a tema dinâmico.")

    def build_ui(self):
        self.page.clean()
        self.page.title = "Sistema de Gestão — Login"

        self.username = ft.TextField(label="Usuário", width=300)
        self.password = ft.TextField(label="Senha", width=300, password=True, can_reveal_password=True)
        self.message = ft.Text("", color=ft.Colors.RED_400)

        btn_login = ft.ElevatedButton("Entrar", width=200, on_click=self.login_action)
        btn_sair = ft.TextButton("Sair", on_click=lambda e: self.page.window_destroy())

        self.page.add(
            ft.Column(
                [
                    ft.Text("🔐 Bem-vindo", size=26, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self.username,
                    self.password,
                    btn_login,
                    self.message,
                    btn_sair,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

    def login_action(self, e):
        user = self.username.value.strip()
        password = self.password.value.strip()

        ok, role = User.autenticar(user, password)
        if ok:
            logger.info(f"Usuário '{user}' autenticado com sucesso.")
            DashboardUI(self.page, user, role)
        else:
            self.message.value = "Usuário ou senha incorretos."
            self.message.color = ft.Colors.RED_400
            self.page.update()


    def open_dashboard(self, username, role):
        logger.info(f"Abrindo dashboard para {username} ({role})")
        self.page.clean()
        DashboardUI(self.page, username, role)

    def register_user(self, e):
        self.message.value = "Cadastro de usuário ainda não implementado."
        self.page.update()
