import flet as ft
from APP.models.usuarios_models import User
from APP.ui.dashboard_ui import DashboardUI
from APP.core.logger import logger
from APP.core.session import session_manager
from APP.core.database import conectar
from APP.ui import style


class LoginUI:
    """Tela de login moderna com controle de sessões e logs."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Sistema de Gestão - Login"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.bgcolor = style.BACKGROUND
        self.page.theme_mode = ft.ThemeMode.DARK

        self.username_field = style.apply_textfield_style(
            ft.TextField(
                label="Usuário",
                width=320,
                prefix_icon=ft.Icons.PERSON_OUTLINE,
                autofocus=True,
            )
        )

        self.password_field = style.apply_textfield_style(
            ft.TextField(
                label="Senha",
                password=True,
                can_reveal_password=True,
                width=320,
                prefix_icon=ft.Icons.LOCK_OUTLINE,
            )
        )

        self.feedback = ft.Text("", color=style.ERROR, size=13)

        self.login_button = style.primary_button("Entrar", on_click=self.login_action)

        self.page.add(
            style.surface_container(
                ft.Column(
                    [
                        ft.Text(
                            "Sistema de Gestão",
                            size=26,
                            weight=ft.FontWeight.BOLD,
                            color=style.TEXT_PRIMARY,
                        ),
                        ft.Text(
                            "Acesse com suas credenciais",
                            size=14,
                            color=style.TEXT_SECONDARY,
                        ),
                        ft.Divider(height=20, color=style.DIVIDER),
                        self.username_field,
                        self.password_field,
                        self.feedback,
                        ft.Container(height=4),
                        self.login_button,
                        style.ghost_button("Esqueci minha senha", on_click=self.forgot_password),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                padding=36,
                width=420,
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

