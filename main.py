import argparse
from pathlib import Path
from platformdirs import user_data_dir, user_documents_dir
from document_manager import DocumentManager
# from g_tags import TagsGraphGenerator
# from g_links import LinksGraphGenerator

#organizar os parsers
def build_parser()->argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="tot — gerador de grafos de notas markdown")
    parser.add_argument("mode", choices=["links", "tags", "all"], help="tipo de grafo")
    return parser

# buscador de vault
def find_vault()->Path:
    # <<<
    #busca vault na pasta documentos
    docs = Path(user_documents_dir())
    if not docs.exists():
        # docs não existe, erro
        raise SystemExit("[!] erro: a pasta Documentos não existe.")

    vaults = [p for p in docs.iterdir() if p.is_dir() and p.suffix == ".tot"]

    if len(vaults) > 1:
        # mais de um vault
        raise SystemExit("[!] erro: múltiplos vaults encontrados")
    if not vaults:
        # nenhum vault
        raise SystemExit("[!] erro: nenhum vault encontrado, crie meu_vault.tot")
    # >>>
    return vaults[0]

def dm_changed(args: argparse.Namespace) -> bool:
    dm = DocumentManager(args.data, args.vault)
    return dm.run()

def gen_tags(args:argparse.Namespace):
    return
def gen_links(args:argparse.Namespace):
    return
def gen_all(args:argparse.Namespace):
    return

def main():
    # <<<
    # pegando args
    parse = build_parser()
    args = parse.parse_args()
    # resolvendo vault
    args.vault = find_vault()
    # resolve paths
    args.output = args.output or (Path(user_documents_dir()) / f"{args.vault.stem}.html")
    Path(user_data_dir("tot")).mkdir(exist_ok=True, parents=True)
    args.data = Path(user_data_dir("tot")) / f"{args.vault.stem}.json"

    # escolha de modo
    match args.mode:
        case "links":
            gen_links(args)
        case "tags":
            gen_tags(args)
        case "all":
            gen_all(args)
    # >>>

