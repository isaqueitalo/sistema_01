import flet as ft
from APP.models.usuarios_models import User
from APP.ui.dashboard_ui import DashboardUI
from APP.core.logger import logger
from APP.core.session import session_manager
from APP.core.database import conectar


class LoginUI:
    """Tela de login moderna com controle de sessões e logs."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Sistema de Gestão - Login"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.bgcolor = ft.Colors.BLUE_GREY_900
        self.page.theme_mode = ft.ThemeMode.DARK

        self.username_field = ft.TextField(
            label="Usuário",
            width=280,
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            autofocus=True,
        )

        self.password_field = ft.TextField(
            label="Senha",
            password=True,
            can_reveal_password=True,
            width=280,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
        )

        self.feedback = ft.Text("", color=ft.Colors.RED_400, size=13)

        self.login_button = ft.ElevatedButton(
            "Entrar",
            width=280,
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
            on_click=self.login_action,
        )

        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("🔐 Sistema de Gestão", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Acesse com suas credenciais", size=14, color=ft.Colors.GREY_400),
                        ft.Divider(height=20, color="transparent"),
                        self.username_field,
                        self.password_field,
                        self.feedback,
                        ft.Divider(height=10, color="transparent"),
                        self.login_button,
                        ft.TextButton(
                            "Esqueci minha senha",
                            on_click=self.forgot_password,
                            style=ft.ButtonStyle(color=ft.Colors.BLUE_200),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                padding=40,
                width=400,
                border_radius=10,
                bgcolor=ft.Colors.BLUE_GREY_800,
                alignment=ft.alignment.center,
                shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK12),
            )
        )

        logger.info("Tela de login minimalista carregada.")

    # =====================================================
    # === AÇÕES DE LOGIN ==================================
    # =====================================================
    def login_action(self, e):
        """Executa autenticação e cria sessão."""
        username = (self.username_field.value or "").strip()
        password = (self.password_field.value or "").strip()

        if not username or not password:
            self.feedback.value = "⚠️ Preencha todos os campos!"
            self.page.update()
            return

        ok, role = User.autenticar(username, password)
        if ok:
            # ✅ Criar sessão
            session_id = session_manager.start_session(username, role)

            # ✅ Registrar login na tabela de logs
            self._registrar_log(username, "login")

            # ✅ Log no sistema
            logger.info(f"Usuário '{username}' autenticado com sucesso (role={role}).")

            # ✅ Limpar tela e abrir dashboard
            self.page.clean()
            DashboardUI(self.page, username, role, session_id=session_id)

        else:
            self.feedback.value = "❌ Usuário ou senha incorretos!"
            logger.warning(f"Tentativa de login inválida: {username}")
            self.page.update()

    # =====================================================
    # === FUNÇÕES AUXILIARES ===============================
    # =====================================================
    def forgot_password(self, e):
        """Exibe mensagem informativa."""
        self.feedback.value = (
            "🔒 A redefinição de senha deve ser feita por um administrador."
        )
        self.page.update()
        logger.info("Usuário acessou 'Esqueci minha senha'.")

    def _registrar_log(self, usuario, acao):
        """Registra eventos de login/logout no banco."""
        try:
            conn = conectar()
            cur = conn.cursor()
            cur.execute("INSERT INTO logs (usuario, acao) VALUES (?, ?)", (usuario, acao))
            conn.commit()
            conn.close()
            logger.debug(f"Log registrado: {usuario} -> {acao}")
        except Exception as e:
            logger.error(f"Erro ao registrar log: {e}", exc_info=True)

