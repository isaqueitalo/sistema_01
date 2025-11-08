import flet as ft
from APP.models.usuarios_models import User
from APP.core.logger import logger


class UsuariosUI:
    """Tela de gerenciamento de usuários (Admin e Master)."""

    def __init__(self, page: ft.Page, usuario_logado: str, voltar_callback=None):
        self.page = page
        self.usuario_logado = usuario_logado  # 🧠 Nome do usuário logado
        self.voltar_callback = voltar_callback
        self.usuario_selecionado = None
        self.build_ui()

    def build_ui(self):
        """Constroi a interface da tela."""
        self.page.clean()
        self.page.title = "Gerenciamento de Usuários"

        # === Campos de cadastro ===
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
                ft.dropdown.Option("admin"),
                ft.dropdown.Option("user"),
            ],
            value="user",
            width=150,
        )

        self.msg = ft.Text("", size=14, color=ft.Colors.BLUE_GREY)

        # === Botões ===
        btn_add = ft.ElevatedButton("➕ Criar Usuário", on_click=self.criar_usuario)
        btn_del = ft.ElevatedButton("🗑️ Excluir Selecionado", on_click=self.confirmar_exclusao)
        btn_back = ft.OutlinedButton("← Voltar", on_click=lambda e: self.voltar_callback())

        # === Tabela de usuários ===
        self.tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Usuário")),
                ft.DataColumn(ft.Text("Função")),
            ],
            rows=[],
            data_row_color={ft.ControlState.HOVERED: ft.Colors.BLUE_50},
        )

        self.atualizar_tabela()

        # === Layout geral ===
        self.page.add(
            ft.Column(
                [
                    ft.Text("👥 Gerenciamento de Usuários", size=22, weight=ft.FontWeight.BOLD),
                    ft.Row([self.username_field, self.password_field, self.role_dropdown, btn_add]),
                    ft.Divider(),
                    ft.Row([btn_del, btn_back], alignment=ft.MainAxisAlignment.CENTER),
                    self.msg,
                    ft.Divider(),
                    self.tabela,
                ],
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        logger.info(f"Tela de gerenciamento de usuários carregada por '{self.usuario_logado}'.")

    # =====================================================
    # === FUNÇÕES PRINCIPAIS ==============================
    # =====================================================

    def atualizar_tabela(self):
        """Atualiza a listagem de usuários no banco."""
        try:
            usuarios = User.listar()
            self.tabela.rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(u[0]))),
                        ft.DataCell(ft.Text(u[1])),
                        ft.DataCell(ft.Text(u[2])),
                    ],
                    on_select_changed=lambda e, u=u: self.selecionar_usuario(u),
                )
                for u in usuarios
            ]
            self.page.update()
        except Exception as err:
            logger.error(f"Erro ao atualizar tabela de usuários: {err}")
            self.msg.value = f"Erro: {err}"
            self.msg.color = ft.Colors.RED
            self.page.update()

    def selecionar_usuario(self, usuario):
        """Seleciona o usuário na tabela."""
        self.usuario_selecionado = usuario
        nome, role = usuario[1], usuario[2]
        self.msg.value = f"✅ Selecionado: {nome} ({role})"
        self.msg.color = ft.Colors.BLUE
        self.page.update()

    def criar_usuario(self, e):
        """Cria novo usuário no sistema."""
        nome = self.username_field.value.strip()
        senha = self.password_field.value.strip()
        role = self.role_dropdown.value

        if not nome or not senha:
            self.msg.value = "⚠️ Preencha todos os campos!"
            self.msg.color = ft.Colors.RED
            self.page.update()
            return

        try:
            User.registrar(nome, senha, role)
            self.msg.value = f"✅ Usuário '{nome}' criado com sucesso!"
            self.msg.color = ft.Colors.GREEN
            logger.info(f"Usuário '{nome}' criado por '{self.usuario_logado}'.")
            self.username_field.value = ""
            self.password_field.value = ""
            self.atualizar_tabela()
            self.page.update()
        except Exception as err:
            self.msg.value = f"❌ Erro: {err}"
            self.msg.color = ft.Colors.RED
            logger.error(f"Erro ao criar usuário: {err}")
            self.page.update()

    # =====================================================
    # === EXCLUSÃO COM CONFIRMAÇÃO ========================
    # =====================================================
    def confirmar_exclusao(self, e):
        """Exibe diálogo de confirmação antes de excluir."""
        if not self.usuario_selecionado:
            self.msg.value = "⚠️ Selecione um usuário antes de excluir!"
            self.msg.color = ft.Colors.RED
            self.page.update()
            return

        nome = self.usuario_selecionado[1]

        # Bloqueio direto antes da confirmação
        if nome == "admin_master":
            self.msg.value = "🚫 O usuário 'admin_master' não pode ser excluído!"
            self.msg.color = ft.Colors.RED
            self.page.update()
            return

        if nome == self.usuario_logado:
            self.msg.value = "🚫 Você não pode excluir a si mesmo!"
            self.msg.color = ft.Colors.RED
            self.page.update()
            return

        # Diálogo de confirmação
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmação de Exclusão", weight=ft.FontWeight.BOLD),
            content=ft.Text(f"Deseja realmente excluir o usuário '{nome}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dlg)),
                ft.ElevatedButton("Excluir", bgcolor=ft.Colors.RED, color=ft.Colors.WHITE,
                                  on_click=lambda e: self.excluir_usuario(nome, dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def excluir_usuario(self, nome, dlg):
        """Realiza a exclusão do usuário após confirmação."""
        try:
            User.excluir(nome, self.usuario_logado)
            dlg.open = False
            self.msg.value = f"🗑️ Usuário '{nome}' excluído com sucesso!"
            self.msg.color = ft.Colors.GREEN
            logger.info(f"Usuário '{nome}' excluído por '{self.usuario_logado}'.")
            self.usuario_selecionado = None
            self.atualizar_tabela()
            self.page.update()
        except Exception as err:
            dlg.open = False
            self.msg.value = f"❌ Erro ao excluir: {err}"
            self.msg.color = ft.Colors.RED
            logger.error(f"Erro ao excluir '{nome}': {err}")
            self.page.update()
