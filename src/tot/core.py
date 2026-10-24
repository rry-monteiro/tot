from pathlib import Path

from platformdirs import user_documents_dir


def scan(path_vault:Path):
    ...

def get_notes(path_vault: Path) -> list:
    """
    Recebe o path do vault e devolve a lista de arquivos
    """
    return [nota.relative_to(path_vault) for nota in path_vault.rglob("*.md")]
    # return list(path_vault.rglob("*.md"))
    

def get_vault() -> Path:
    """
    Entra nos documentos e procura o vault marcado com o sufixo .tot,
    retorna erro caso não encontre ou encontre múltiplos
    """
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
        raise SystemExit(
            "erro: nenhum vault encontrado, crie 'Documentos/meu_vault.tot/'"
        )
    return vaults[0]



