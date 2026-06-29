import argparse
from pathlib import Path
from platformdirs import user_data_dir, user_documents_dir
from document_manager import DocumentManager

#organizar os parsers
def build_parser()->argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="tot — gerador de grafos de notas markdown")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--links", action="store_true", help="Só grafo de links")
    group.add_argument("-t", "--tags", action="store_true", help="Só grafo de tags")
    group.add_argument("-a", "--all", action="store_true", help="Cria os dois tipos de grafo")
    return parser

def find_vault():
    documents = Path(user_documents_dir())
    if not documents.exists():
        print("[!] erro: a pasta Documentos não existe.")

    vaults = [p for p in documents.iterdir() if p.is_dir() and p.suffix == ".tot"]
    
    if len(vaults) > 1:
        print("[!] erro: multiplos vaults encontrados")
    elif not vaults:
        print("[!] erro: nenhum vault encontrado, crie meu_vault.tot")
    else:
        return vaults[0]

def main() -> None:
    find_vault()
    # defaults
    parser = build_parser()
    args = parser.parse_args()
    # caso não tenha args
    if not (args.links or args.tags or args.all):
        parser.error("Você precisa escolher um tipo de grafo. Use -l, -t ou -a")

    # escolhas de tipo de grafo
    if args.links:
        pass
    elif args.tags:
        pass
    elif args.all:
        pass

main()

