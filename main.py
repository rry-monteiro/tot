import argparse
from pathlib import Path
from platformdirs import user_data_dir, user_documents_dir
from document_manager import DocumentManager
from g_tags import TagsGraphGenerator
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

# função pra ver se o vault mudou
def dm_changed(args: argparse.Namespace) -> bool:
    dm = DocumentManager(args.data, args.vault)
    return dm.run()

#comandos de geração
def gen_tags(args:argparse.Namespace):
    if not dm_changed(args):
        print("[~] info: nenhuma mudança detectada no vault")
        return
    tg = TagsGraphGenerator(args.output, args.data, args.vault)
    tg.render()
    print(f"[+] info: grafo de tags em {args.output}")

def gen_links(args:argparse.Namespace):
    if not dm_changed(args):
        print("[~] info: nenhuma mudança detectada no vault")
        return

def gen_all(args:argparse.Namespace):
    if not dm_changed(args):
        print("[~] info: nenhuma mudança detectada no vault")
        return

def main():
    # <<<
    # pegando args
    parse = build_parser()
    args = parse.parse_args()
    # resolvendo vault
    args.vault = find_vault()
    # resolve paths
    args.output = (Path(user_documents_dir()) / f"{args.vault.name}.html")
    Path(user_data_dir("tot")).mkdir(exist_ok=True, parents=True)
    args.data = Path(user_data_dir("tot")) / f"{args.vault.name}.json"

    # escolha de modo
    match args.mode:
        case "links":
            gen_links(args)
        case "tags":
            gen_tags(args)
        case "all":
            gen_all(args)
    # >>>

if __name__ == "__main__":
    main()
