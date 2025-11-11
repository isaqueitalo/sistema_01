import flet as ft
from APP.models.usuarios_models import User
from APP.core.logger import logger
from APP.ui import style


class UsuariosUI:
    """Tela de gerenciamento de usuários"""

    def __init__(self, page: ft.Page, voltar_callback=None):
        self.page = page
        self.voltar_callback = voltar_callback
        self.build_ui()
        logger.info(f"Tela de gerenciamento de usuários carregada por '{voltar_callback}'.")

    # ============================================================
    # === INTERFACE ==============================================
    # ============================================================
    def build_ui(self):
        self.page.clean()
        self.page.title = "Gerenciamento de Usuários"
        self.page.bgcolor = style.BACKGROUND

        titulo = ft.Text(
            "👥 Gerenciamento de Usuários",
            size=22,
            weight=ft.FontWeight.BOLD,
            color=style.TEXT_PRIMARY,
        )

        # Campos
        self.username_field = style.apply_textfield_style(
            ft.TextField(label="Usuário", width=260)
        )
        self.password_field = style.apply_textfield_style(
            ft.TextField(
                label="Senha",
                password=True,
                can_reveal_password=True,
                width=260,
            )
        )
        self.role_dropdown = ft.Dropdown(
            label="Função",
            options=[
                ft.dropdown.Option("admin_master"),
                ft.dropdown.Option("admin"),
                ft.dropdown.Option("vendedor"),
            ],
            value="vendedor",
            width=220,
            bgcolor=style.SURFACE_ALT,
            border_radius=8,
            border_color=style.BORDER,
            focused_border_color=style.ACCENT,
            color=style.TEXT_PRIMARY,
            text_style=ft.TextStyle(color=style.TEXT_PRIMARY),
            label_style=ft.TextStyle(color=style.TEXT_SECONDARY),
            hint_style=ft.TextStyle(color=style.TEXT_SECONDARY),
        )

        # Mensagem
        self.message = ft.Text("", color=style.TEXT_SECONDARY)

        # Botões
        btn_add = style.primary_button(
            "Adicionar Usuário",
            icon=ft.Icons.PERSON_ADD_ALT,
            on_click=self.adicionar_usuario,
        )
        btn_voltar = style.ghost_button(
            "Voltar",
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            on_click=lambda e: self.voltar_callback() if callable(self.voltar_callback) else self.voltar_login(),
        )

        # Tabela
        self.tabela = style.stylize_datatable(
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Usuário")),
                    ft.DataColumn(ft.Text("Função")),
                ],
                rows=[],
            )
        )

        # Layout principal
        layout = ft.Column(
            [
                titulo,
                ft.Row(
                    [self.username_field, self.password_field, self.role_dropdown],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                    wrap=True,
                ),
                ft.Row([btn_add, btn_voltar], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
                self.message,
                ft.Divider(color=style.DIVIDER),
                ft.Text(
                    "📋 Usuários Cadastrados",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=style.TEXT_PRIMARY,
                ),
                self.tabela,
            ],
            spacing=18,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        )
        self.page.add(
            ft.Container(
                content=style.surface_container(layout, padding=28),
                padding=ft.Padding(24, 24, 24, 24),
                expand=True,
                alignment=ft.alignment.center,
            )
        )

        self.atualizar_tabela()

    # ============================================================
    # === FUNÇÕES ================================================
    # ============================================================
    def atualizar_tabela(self):
        """Atualiza a tabela de usuários"""
        usuarios = User.listar()
        logger.debug(f"{len(usuarios)} usuários listados.")
        self.tabela.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(u[0]), color=style.TEXT_SECONDARY)),
                    ft.DataCell(ft.Text(u[1], color=style.TEXT_PRIMARY)),
                    ft.DataCell(ft.Text(u[2], color=style.TEXT_SECONDARY)),
                ]
            ) for u in usuarios
        ]
        self.page.update()

    def adicionar_usuario(self, e):
        """Adiciona novo usuário"""
        nome = self.username_field.value.strip()
        senha = self.password_field.value.strip()
        role = self.role_dropdown.value

        if not nome or not senha:
            self.message.value = "Preencha todos os campos."
            self.message.color = style.ERROR
            self.page.update()
            return

        try:
            User.registrar(nome, senha, role)
            self.message.value = f"✅ Usuário '{nome}' criado com sucesso."
            self.message.color = style.SUCCESS
            logger.info(f"Usuário '{nome}' criado com função '{role}'.")
            self.atualizar_tabela()
        except Exception as err:
            self.message.value = f"Erro: {err}"
            self.message.color = style.ERROR
            logger.error(f"Erro ao criar usuário: {err}")

        self.page.update()

    def voltar_login(self):
        """Retorna para o login se não houver callback definido."""
        from APP.ui.login_ui import LoginUI
        self.page.clean()
        LoginUI(self.page)
