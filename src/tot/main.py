import argparse

from . import core, daemon


# organizar os parsers
def build_parser() -> argparse.ArgumentParser:
    """constrói o parser com as flags e suas descrições e retorna o objeto parser"""
    # <<<
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
    # >>>
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.daemon:
        vault = core.get_vault()
        daemon.run(vault)
    elif args.install:
        print(args.install)
    elif args.uninstall:
        print(args.uninstall)
    else:
        ...


if __name__ == "__main__":
    main()
