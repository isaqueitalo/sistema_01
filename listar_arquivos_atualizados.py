from __future__ import annotations

import json
from pathlib import Path

# Lista dos principais arquivos atualizados mencionados nas últimas alterações
UPDATED_FILES = [
    Path("APP/ui/style.py"),
    Path("APP/ui/login_ui.py"),
    Path("APP/ui/dashboard_ui.py"),
    Path("APP/ui/produtos_ui.py"),
    Path("APP/ui/vendas_ui.py"),
    Path("APP/ui/usuarios_ui.py"),
    Path("APP/ui/relatorios_ui.py"),
    Path("APP/ui/logs_viewer.py"),
    Path("APP/models/produtos_models.py"),
    Path("APP/models/vendas_models.py"),
    Path("APP/models/usuarios_models.py"),
]


def resolve_workspace() -> Path:
    """Retorna a raiz do projeto (onde este script está localizado)."""

    return Path(__file__).resolve().parent


def build_listing() -> list[dict[str, str]]:
    """Gera dados serializáveis contendo caminhos absolutos e relativos."""

    root = resolve_workspace()
    listing = []
    for relative in UPDATED_FILES:
        absolute = root / relative
        listing.append(
            {
                "relative_path": str(relative),
                "absolute_path": str(absolute),
                "exists_on_disk": absolute.exists(),
            }
        )
    return listing


def main() -> None:
    """Imprime um resumo em JSON para facilitar a verificação no VS Code."""

    print(
        json.dumps(
            {
                "workspace_root": str(resolve_workspace()),
                "updated_files": build_listing(),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
