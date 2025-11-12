import flet as ft
from APP.models.usuarios_models import User
from APP.core.logger import logger
from APP.ui import style


class UsuariosUI:
    """Tela de gerenciamento de usuários com visual padronizado e ações administrativas."""

    def __init__(self, page: ft.Page, voltar_callback=None, current_role: str | None = None, current_user: str | None = None):
        self.page = page
        self.voltar_callback = voltar_callback
        self.current_role = current_role or "vendedor"
        self.current_user = current_user or ""
        self.can_manage_roles = self.current_role == "admin_master"

        self.page.clean()
        self.page.title = "Usuários e Permissões"
        self.page.bgcolor = style.BACKGROUND

        self._build_ui()
        logger.info("Tela de usuários carregada (%s).", self.current_role)

    def _build_ui(self):
        titulo = ft.Text(
            "👥 Usuários e Permissões",
            size=22,
            weight=ft.FontWeight.BOLD,
            color=style.TEXT_DARK,
        )

        self.username_field = style.apply_textfield_style(
            ft.TextField(label="Usuário", width=240, autofocus=True)
        )
        self.password_field = style.apply_textfield_style(
            ft.TextField(label="Senha", password=True, can_reveal_password=True, width=240)
        )
        self.role_dropdown = ft.Dropdown(
            label="Função",
            options=[
                ft.dropdown.Option("vendedor", "Vendedor"),
                ft.dropdown.Option("admin", "Admin"),
                ft.dropdown.Option("admin_master", "Admin Master"),
            ],
            value="vendedor",
            width=220,
            bgcolor=style.PANEL_LIGHT,
            border_radius=10,
            border_color=style.BORDER,
            focused_border_color=style.ACCENT,
            text_style=ft.TextStyle(color=style.TEXT_DARK, weight=ft.FontWeight.W_500),
            label_style=ft.TextStyle(color=style.TEXT_MUTED),
            hint_style=ft.TextStyle(color=style.TEXT_MUTED),
        )

        self.message = ft.Text("", color=style.TEXT_MUTED)

        btn_add = style.primary_button("Adicionar usuário", icon=ft.Icons.PERSON_ADD, on_click=self.adicionar_usuario)
        btn_voltar = style.ghost_button(
            "Voltar",
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda _: self.voltar_callback() if callable(self.voltar_callback) else None,
        )

        columns = [
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Usuário")),
            ft.DataColumn(ft.Text("Função")),
        ]
        if self.can_manage_roles:
            columns.append(ft.DataColumn(ft.Text("Ações")))

        self.tabela = style.stylize_datatable(ft.DataTable(columns=columns, rows=[]))

        layout = ft.Column(
            [
                titulo,
                ft.Text("Cadastre, edite funções ou remova usuários do sistema.", color=style.TEXT_MUTED),
                ft.Row(
                    [self.username_field, self.password_field, self.role_dropdown],
                    spacing=12,
                    wrap=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row([btn_add, btn_voltar], spacing=12, alignment=ft.MainAxisAlignment.CENTER),
                self.message,
                ft.Divider(color=style.DIVIDER),
                ft.Text("Usuários cadastrados", size=18, weight=ft.FontWeight.W_600, color=style.TEXT_DARK),
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

    def atualizar_tabela(self):
        usuarios = User.listar()
        rows = []
        for uid, nome, role in usuarios:
            cells = [
                ft.DataCell(ft.Text(str(uid), color=style.TEXT_MUTED)),
                ft.DataCell(ft.Text(nome, color=style.TEXT_DARK)),
                ft.DataCell(ft.Text(role, color=style.TEXT_MUTED)),
            ]

            if self.can_manage_roles:
                disabled = nome == "admin_master"
                actions = ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            tooltip="Editar função",
                            icon_color=style.ACCENT,
                            disabled=disabled,
                            on_click=self._make_edit_handler(nome, role),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="Excluir",
                            icon_color=style.ERROR,
                            disabled=disabled or nome == self.current_user,
                            on_click=self._make_delete_handler(nome),
                        ),
                    ],
                    spacing=0,
                )
                cells.append(ft.DataCell(actions))

            rows.append(ft.DataRow(cells=cells))

        self.tabela.rows = rows
        self.page.update()

    def adicionar_usuario(self, _):
        nome = (self.username_field.value or "").strip()
        senha = (self.password_field.value or "").strip()
        role = self.role_dropdown.value

        if not nome or not senha:
            self._set_message("Preencha usuário e senha.", erro=True)
            return

        try:
            User.registrar(nome, senha, role)
            self._set_message(f"Usuário '{nome}' criado com sucesso.", sucesso=True)
            self.username_field.value = ""
            self.password_field.value = ""
            self.role_dropdown.value = "vendedor"
            self.atualizar_tabela()
        except Exception as err:
            self._set_message(str(err), erro=True)
            logger.error("Erro ao adicionar usuário: %s", err)

        self.page.update()

    def _confirmar_exclusao(self, nome):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Excluir usuário"),
            content=ft.Text(f"Deseja realmente excluir '{nome}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=self._fechar_dialogo),
                style.danger_button("Excluir", icon=ft.Icons.DELETE, on_click=lambda _: self._excluir_usuario(nome)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._abrir_dialogo(dialog)

    def _excluir_usuario(self, nome):
        try:
            User.excluir(nome, self.current_user)
            self._set_message(f"Usuário '{nome}' removido.", sucesso=True)
            logger.info("Usuário '%s' removido por '%s'.", nome, self.current_user)
            self.atualizar_tabela()
        except Exception as err:
            self._set_message(str(err), erro=True)
            logger.error("Erro ao excluir usuário: %s", err)
        finally:
            self._fechar_dialogo()

    def _abrir_dialogo_role(self, nome, role_atual):
        dropdown = ft.Dropdown(
            label=f"Novo papel para {nome}",
            width=260,
            bgcolor=style.PANEL_LIGHT,
            border_radius=10,
            border_color=style.BORDER,
            focused_border_color=style.ACCENT,
            value=role_atual,
            options=[
                ft.dropdown.Option("vendedor", "Vendedor"),
                ft.dropdown.Option("admin", "Admin"),
            ],
        )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar função"),
            content=dropdown,
            actions=[
                ft.TextButton("Cancelar", on_click=self._fechar_dialogo),
                style.primary_button(
                    "Salvar",
                    icon=ft.Icons.SAVE,
                    on_click=lambda _: self._salvar_role(nome, dropdown.value),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._abrir_dialogo(dialog)

    def _salvar_role(self, nome, nova_role):
        try:
            User.atualizar_role(nome, nova_role, self.current_user)
            self._set_message(f"Função de '{nome}' atualizada para {nova_role}.", sucesso=True)
            logger.info("Função de %s alterada para %s por %s.", nome, nova_role, self.current_user)
            self.atualizar_tabela()
        except Exception as err:
            self._set_message(str(err), erro=True)
            logger.error("Erro ao atualizar função: %s", err)
        finally:
            self._fechar_dialogo()

    def _abrir_dialogo(self, dialog: ft.AlertDialog):
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _fechar_dialogo(self, _=None):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def _set_message(self, texto, *, sucesso=False, erro=False):
        if sucesso:
            self.message.color = style.SUCCESS
        elif erro:
            self.message.color = style.ERROR
        else:
            self.message.color = style.TEXT_MUTED
        self.message.value = texto

    def _make_edit_handler(self, nome, role_atual):
        def handler(_):
            self._abrir_dialogo_role(nome, role_atual)
        return handler

    def _make_delete_handler(self, nome):
        def handler(_):
            self._confirmar_exclusao(nome)
        return handler
