"""Paleta e componentes reutilizáveis para o tema escuro minimalista."""

import flet as ft

# === Paleta base ===
BACKGROUND = "#0B0F16"
SURFACE = "#161C23"
SURFACE_ALT = "#1F2733"
ACCENT = "#3F8EFC"
ACCENT_HOVER = "#5AA6FF"
TEXT_PRIMARY = "#ECEFF4"
TEXT_SECONDARY = "#9BA5B7"
SUCCESS = "#4ADE80"
ERROR = "#F87171"
DIVIDER = "#1F2530"
BORDER = "#202837"

_BUTTON_SHAPE = ft.RoundedRectangleBorder(radius=8)


def apply_textfield_style(field: ft.TextField) -> ft.TextField:
    """Aplica o estilo padrão minimalista a um TextField existente."""

    field.filled = True
    field.bgcolor = SURFACE_ALT
    field.border_radius = 8
    field.border_color = BORDER
    field.focused_border_color = ACCENT
    field.cursor_color = ACCENT
    field.color = TEXT_PRIMARY
    field.label_style = ft.TextStyle(color=TEXT_SECONDARY)
    field.text_style = ft.TextStyle(color=TEXT_PRIMARY)
    field.hint_style = ft.TextStyle(color=TEXT_SECONDARY)
    return field


def primary_button(label: str, *, icon: str | None = None, on_click=None) -> ft.ElevatedButton:
    """Cria um botão principal consistente com o tema escuro minimalista."""

    return ft.ElevatedButton(
        label,
        icon=icon,
        on_click=on_click,
        bgcolor=ACCENT,
        color=TEXT_PRIMARY,
        height=44,
        style=ft.ButtonStyle(
            shape=_BUTTON_SHAPE,
            padding=ft.Padding(22, 0, 22, 0),
            elevation=0,
            bgcolor={ft.ControlState.HOVERED: ACCENT_HOVER},
        ),
    )


def danger_button(label: str, *, icon: str | None = None, on_click=None) -> ft.ElevatedButton:
    """Botão para ações destrutivas (excluir, sair)."""

    return ft.ElevatedButton(
        label,
        icon=icon,
        on_click=on_click,
        bgcolor=ERROR,
        color=TEXT_PRIMARY,
        height=44,
        style=ft.ButtonStyle(
            shape=_BUTTON_SHAPE,
            padding=ft.Padding(22, 0, 22, 0),
            elevation=0,
            bgcolor={ft.ControlState.HOVERED: "#FF7F88"},
        ),
    )


def ghost_button(label: str, *, icon: str | None = None, on_click=None) -> ft.TextButton:
    """Botão secundário discreto para ações de retorno/apoio."""

    return ft.TextButton(
        label,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
             color={ft.ControlState.DEFAULT: TEXT_SECONDARY, ft.ControlState.HOVERED: TEXT_PRIMARY},
            shape=_BUTTON_SHAPE,
            padding=ft.Padding(18, 0, 18, 0),
            overlay_color={ft.ControlState.HOVERED: "#ffffff20"},
        ),
    )


def surface_container(content: ft.Control, *, width: float | None = None, padding: int = 24) -> ft.Container:
    """Container com borda sutil usado como cartão/painel."""

    return ft.Container(
        content=content,
        bgcolor=SURFACE,
        border_radius=12,
        padding=padding,
        width=width,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color="#00000020", spread_radius=1),
    )


def stylize_datatable(table: ft.DataTable) -> ft.DataTable:
    """Aplica o esquema de cores do tema à DataTable."""

    table.bgcolor = SURFACE
    table.heading_row_color = SURFACE_ALT
    table.heading_text_style = ft.TextStyle(color=TEXT_PRIMARY, weight=ft.FontWeight.W_600)
    table.data_text_style = ft.TextStyle(color=TEXT_SECONDARY)
    table.divider_thickness = 0
    table.border = ft.border.all(1, BORDER)
    return table
