import hashlib
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from platformdirs import user_documents_dir

VAULT: Path | None = None
REGEX_TAGS = re.compile(r"tags:\s*\[([^\]]*)\]")
REGEX_LINKS = re.compile(r'\[[^\]]+\]\(([^)#\s"]+\.md)')


def hash_is_equal(files: dict, old_relative_path: str, new_path: str):
    texto = Path(new_path).read_text(encoding="utf-8", errors="replace")
    h_novo = hashlib.blake2b(texto.encode(), digest_size=16).hexdigest()
    return files[old_relative_path]["hash"] == h_novo


def parser(file: Path) -> tuple:
    """
    passa o regex capturando links e tags do arquivo, calcula o hash
    """
    assert VAULT is not None

    text = file.read_text(encoding="utf-8", errors="replace")

    h = hashlib.blake2b(text.encode(), digest_size=16).hexdigest()

    # tags
    str_tags = REGEX_TAGS.findall(text)
    tags = [
        tag for grupo in str_tags for item in grupo.split(",") if (tag := item.strip())
    ]

    # links
    brute_links = REGEX_LINKS.findall(text)
    links = []

    for link in brute_links:
        absolute = (file.parent / link).resolve()
        relative = absolute.relative_to(VAULT)
        links.append(str(relative))

    return str(file.relative_to(VAULT)), {"tags": tags, "links": links, "hash": h}


def scan() -> dict:
    """
    scaneia o vault por completo e devolve a estrutura base dos graficos de tags e notas
    """
    assert VAULT is not None
    notes = get_notes(relative=False)
    with ThreadPoolExecutor(max_workers=15) as executor:
        files = dict(executor.map(parser, notes))

    return {"files": files}


def get_notes(relative: bool) -> list:
    """
    Recebe o path do vault e devolve a lista de arquivos
    """
    assert VAULT is not None

    if relative:
        return [nota.relative_to(VAULT) for nota in VAULT.rglob("*.md")]
    else:
        return list(VAULT.rglob("*.md"))


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
