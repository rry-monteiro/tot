import re
import socket
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from platformdirs import user_documents_dir, user_runtime_dir

VAULT: Path | None = None
REGEX_TAGS = re.compile(r"tags:\s*\[([^\]]*)\]")
REGEX_LINKS = re.compile(r'\[[^\]]+\]\(([^)#\s"]+\.md)')
SOCK: Path = Path(user_runtime_dir("tot")) / "tot.sock"


def parser(file: Path) -> tuple:
    """
    passa o regex capturando links e tags do arquivo, calcula o hash
    """
    assert VAULT is not None

    text = file.read_text(encoding="utf-8", errors="replace")

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

    return str(file.relative_to(VAULT)), {"tags": tags, "links": links}


def build_graph(data: str):
    template_path = Path(__file__).resolve().parent / "d3.html"
    template = template_path.read_text(encoding="utf-8")
    graph = template.replace("/*INSERT_DATA*/", data)
    Path(Path(user_documents_dir())/"tot.graph.html").write_text(graph, encoding="utf-8")


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

def get_files()->dict:
    # caso o daemon esteja ligado
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect(str(SOCK))
            files = json.loads(s.makefile("r", encoding="utf-8").readline())
    # caso esteja desligado
    except (FileNotFoundError, ConnectionRefusedError):
        print("tot desligado, ligue com 'tot system daemon'")
        files = scan()["files"]
    # retorna o files de qualquer jeito
    return files
