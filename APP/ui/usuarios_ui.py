import flet as ft
from APP.models.usuarios_models import User
from APP.core.logger import logger


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

        titulo = ft.Text("👥 Gerenciamento de Usuários", size=22, weight=ft.FontWeight.BOLD)

        # Campos
        self.username_field = ft.TextField(label="Usuário", width=250)
        self.password_field = ft.TextField(
            label="Senha",
            password=True,
            can_reveal_password=True,
            width=250
        )
        self.role_dropdown = ft.Dropdown(
            label="Função",
            options=[
                ft.dropdown.Option("admin_master"),
                ft.dropdown.Option("admin"),
                ft.dropdown.Option("vendedor"),
            ],
            value="vendedor",
            width=200,
        )

        # Mensagem
        self.message = ft.Text("", color=ft.Colors.RED_400)

        # Botões
        btn_add = ft.ElevatedButton("Adicionar Usuário", on_click=self.adicionar_usuario)
        btn_voltar = ft.OutlinedButton(
            "← Voltar",
            on_click=lambda e: self.voltar_callback() if callable(self.voltar_callback) else self.voltar_login()
        )

        # Tabela
        self.tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Usuário")),
                ft.DataColumn(ft.Text("Função")),
            ],
            rows=[],
        )

        # Layout principal
        self.page.add(
            ft.Column(
                [
                    titulo,
                    ft.Row([self.username_field, self.password_field, self.role_dropdown]),
                    ft.Row([btn_add, btn_voltar]),
                    self.message,
                    ft.Divider(),
                    ft.Text("📋 Usuários Cadastrados", size=18, weight=ft.FontWeight.BOLD),
                    self.tabela,
                ],
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
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
                    ft.DataCell(ft.Text(str(u[0]))),
                    ft.DataCell(ft.Text(u[1])),
                    ft.DataCell(ft.Text(u[2])),
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
            self.message.color = ft.Colors.RED_400
            self.page.update()
            return

        try:
            User.registrar(nome, senha, role)
            self.message.value = f"✅ Usuário '{nome}' criado com sucesso."
            self.message.color = ft.Colors.GREEN_400
            logger.info(f"Usuário '{nome}' criado com função '{role}'.")
            self.atualizar_tabela()
        except Exception as err:
            self.message.value = f"Erro: {err}"
            self.message.color = ft.Colors.RED_400
            logger.error(f"Erro ao criar usuário: {err}")

        self.page.update()

    def voltar_login(self):
        """Retorna para o login se não houver callback definido."""
        from APP.ui.login_ui import LoginUI
        self.page.clean()
        LoginUI(self.page)
