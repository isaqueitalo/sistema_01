"""Paleta e componentes reutilizáveis inspirados em PDVs roxos (ex.: SIGE Lite)."""

import flet as ft

# === Paleta base ===
BACKGROUND = "#0B0F16"
SURFACE = "#161C23"
SURFACE_ALT = "#1F2733"
ACCENT = "#7A2CFF"
ACCENT_HOVER = "#8E48FF"
TEXT_PRIMARY = "#ECEFF4"
TEXT_SECONDARY = "#9BA5B7"
TEXT_DARK = "#1D1233"
TEXT_MUTED = "#6F6892"
SUCCESS = "#39D98A"
ERROR = "#F65A83"
DIVIDER = "#1F2530"
BORDER = "#202837"
PANEL_LIGHT = "#FFFFFF"
PANEL_MUTED = "#F5F4FB"

_BUTTON_SHAPE = ft.RoundedRectangleBorder(radius=10)


def apply_textfield_style(field: ft.TextField, *, variant: str = "light") -> ft.TextField:
    """Aplica o estilo padrão baseado em cartões escuros ou claros."""

    field.filled = True
    field.border_radius = 10
    field.focused_border_color = ACCENT
    field.cursor_color = ACCENT

    if variant == "light":
        field.bgcolor = PANEL_LIGHT
        field.border_color = "#D9CCFF"
        field.color = TEXT_DARK
        field.label_style = ft.TextStyle(color=TEXT_MUTED)
        field.text_style = ft.TextStyle(color=TEXT_DARK, weight=ft.FontWeight.W_500)
        field.hint_style = ft.TextStyle(color=TEXT_MUTED)
    else:
        field.bgcolor = SURFACE_ALT
        field.border_color = BORDER
        field.color = TEXT_PRIMARY
        field.label_style = ft.TextStyle(color=TEXT_SECONDARY)
        field.text_style = ft.TextStyle(color=TEXT_PRIMARY)
        field.hint_style = ft.TextStyle(color=TEXT_SECONDARY)

    return field


def primary_button(label: str, *, icon: str | None = None, on_click=None, bgcolor: str | None = None) -> ft.ElevatedButton:
    """Cria um botão principal com cantos arredondados."""

    base_color = bgcolor or ACCENT
    return ft.ElevatedButton(
        label,
        icon=icon,
        on_click=on_click,
        bgcolor=base_color,
        color=TEXT_PRIMARY,
        height=48,
        style=ft.ButtonStyle(
            shape=_BUTTON_SHAPE,
            padding=ft.Padding(24, 0, 24, 0),
            elevation=0,
            bgcolor={ft.ControlState.HOVERED: ACCENT_HOVER},
        ),
    )


def flat_shortcut_button(
    label: str,
    shortcut: str,
    *,
    icon: str | None = None,
    color: str = ACCENT,
    on_click=None,
    selected: bool = False,
    col: dict | None = None,
    width: int | None = None,
) -> ft.Container:
    """Tile colorido para atalhos de teclado (F-keys)."""
    return ft.Container(
        bgcolor=color,
        border_radius=12,
        padding=ft.Padding(16, 14, 16, 14),
        width=140 if width is None else width,
        col=col or {"xs": 6, "sm": 4, "md": 3, "lg": 2},
        border=ft.border.all(2, TEXT_PRIMARY) if selected else None,
        content=ft.Column(
            [
                ft.Text(shortcut, size=12, color=TEXT_SECONDARY, weight=ft.FontWeight.W_600),
                ft.Row(
                    [
                        ft.Icon(icon, size=20, color=TEXT_PRIMARY) if icon else ft.Container(width=0),
                        ft.Text(label, color=TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                    ],
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=4,
        ),
        ink=True,
        on_click=on_click,
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
            bgcolor={ft.ControlState.HOVERED: "#FF7F9A"},
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
            overlay_color={ft.ControlState.HOVERED: "#ffffff30"},
        ),
    )


def surface_container(content: ft.Control, *, width: float | None = None, padding: int = 24, bgcolor: str | None = None) -> ft.Container:
    """Container com borda sutil usado como cartão/painel."""

    return ft.Container(
        content=content,
        bgcolor=bgcolor or PANEL_LIGHT,
        border_radius=18,
        padding=padding,
        width=width,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color="#00000020", spread_radius=1),
    )


def summary_card(title: str, value: str, *, subtitle: str | None = None, accent: str = ACCENT) -> ft.Container:
    """Cartão informativo usado em PDV para totals/status."""
    return ft.Container(
        bgcolor=PANEL_MUTED,
        border_radius=16,
        padding=ft.Padding(20, 16, 20, 16),
        border=ft.border.all(1, "#E0D5FF"),
        content=ft.Column(
            [
                ft.Text(title, size=13, color=TEXT_MUTED, weight=ft.FontWeight.W_600),
                ft.Text(value, size=22, color=accent, weight=ft.FontWeight.BOLD),
                ft.Text(subtitle or "", size=12, color=TEXT_MUTED),
            ],
            spacing=4,
        ),
    )


def stylize_datatable(table: ft.DataTable, *, header_bg: str | None = None, variant: str = "light") -> ft.DataTable:
    """Aplica o esquema de cores à DataTable."""

    if variant == "light":
        table.bgcolor = PANEL_LIGHT
        table.heading_row_color = header_bg or PANEL_MUTED
        table.heading_text_style = ft.TextStyle(color=TEXT_DARK, weight=ft.FontWeight.W_600)
        table.data_text_style = ft.TextStyle(color=TEXT_DARK)
        table.border = ft.border.all(1, "#E0D5FF")
    else:
        table.bgcolor = SURFACE
        table.heading_row_color = header_bg or SURFACE_ALT
        table.heading_text_style = ft.TextStyle(color=TEXT_PRIMARY, weight=ft.FontWeight.W_600)
        table.data_text_style = ft.TextStyle(color=TEXT_SECONDARY)
        table.border = ft.border.all(1, BORDER)

    table.divider_thickness = 0
    return table
