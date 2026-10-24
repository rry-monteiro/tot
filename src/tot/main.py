import argparse
from pathlib import Path

from platformdirs import user_data_dir, user_documents_dir


# organizar os parsers
def build_parser() -> argparse.ArgumentParser:
    """constrói o parser com as flags e suas descrições e retorna o objeto parser"""
    parser = argparse.ArgumentParser(
        description="tot — gerador de grafos de notas markdown"
    )
    # parser.add_argument("mode", choices=["links", "tags", "all"], help="tipo de grafo")
    parser.add_argument(
        "--daemon", action="store_true", help="Sobe o daemon no sistema"
    )
    parser.add_argument(
        "--install", action="store_true", help="Instala o .desktop no autostart"
    )
    parser.add_argument(
        "--uninstall", action="store_true", help="Remove o .desktop do autostart"
    )
    return parser


# buscador de vault
def find_vault() -> Path:
    """
    Entra nos documentos e procura o vault marcado com o sufixo .tot,
    retorna erro caso não encontre ou encontre múltiplos
    """
    # <<<
    # busca vault na pasta documentos
    docs = Path(user_documents_dir())
    if not docs.exists():
        raise SystemExit("erro: a pasta Documentos não existe")

    # buscando
    vaults = [p for p in docs.iterdir() if p.is_dir() and p.suffix == ".tot"]

    # mais de 1 vault / nenhum vault
    if len(vaults) > 1:
        raise SystemExit("erro: múltiplos vaults encontrados.")
    if not vaults:
        raise SystemExit("erro: nenhum vault encontrado, crie 'Documentos/meu_vault.tot/'")
    # >>>
    return vaults[0]

def main():
    # <<<
    ...
    # >>>


if __name__ == "__main__":
    main()
