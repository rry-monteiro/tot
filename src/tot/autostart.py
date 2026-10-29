import shutil
import sys
from pathlib import Path

from platformdirs import user_config_dir

DESTINO: Path = Path(user_config_dir()) / "autostart" / "tot.desktop"

def install() -> None:

    exe = Path(sys.argv[0]).absolute()
    if ".venv" in exe.parts:
        print("rode 'tot system install' pelo comando instalado (uv tool install), não pelo uv run", file=sys.stderr,)
        sys.exit(1)

    conteudo = f"""[Desktop Entry]
Type=Application
Name=tot
Comment=Gerador de gráficos de notas markdown
Exec="{exe}" system daemon
Terminal=false
X-GNOME-Autostart-enabled=true
"""
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(conteudo, encoding="utf-8")
    print(f"instalado em {DESTINO}")


def uninstall() -> None:
    DESTINO.unlink(missing_ok=True)
    print("autostart removido")
