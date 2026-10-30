import argparse

from . import autostart, core, daemon


# organizar os parsers
def build_parser() -> argparse.ArgumentParser:
    """constrói o parser com as flags e suas descrições e retorna o objeto parser"""
    # <<<
    parser = argparse.ArgumentParser(
        description="tot — gerador de grafos de notas markdown"
    )
    parser.add_argument(
        "-t", "--find-tag", type=str, metavar="TAG", help="Busca uma tag"
    )
    parser.add_argument(
        "-n", "--find-note", type=str, metavar="NOTA", help="Busca uma nota"
    )
    parser.add_argument(
        "-m", "--metrics", action="store_true", help="Mostra métricas gerais"
    )

    sub = parser.add_subparsers(dest="cmd")
    system = sub.add_parser("system", help="Ações do sistema")
    system_sub = system.add_subparsers(dest="action", required=True)
    system_sub.add_parser("daemon", help="Sobe o daemon no sistema")
    system_sub.add_parser("install", help="Instala o .desktop no autostart")
    system_sub.add_parser("uninstall", help="Remove o .desktop do autostart")
    # >>>
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    consulta = args.find_tag is not None or args.find_note is not None or args.metrics

    core.VAULT = core.get_vault()

    if args.cmd == "system":
        if consulta:
            parser.error("'system' não pode ser usado com -t, -n ou -m")
        if args.action == "daemon":
            daemon.run()
        elif args.action == "install":
            autostart.install()
        elif args.action == "uninstall":
            autostart.uninstall()
    elif consulta:
        if args.find_tag is not None:
            pass
        if args.find_note is not None:
            pass
        if args.metrics:
            pass
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
