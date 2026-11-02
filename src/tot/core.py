import json
import re
import socket
from collections import Counter
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
    Path(Path(user_documents_dir()) / "tot.graph.html").write_text(
        graph, encoding="utf-8"
    )


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


def get_files() -> dict:
    # caso o daemon esteja ligado
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect(str(SOCK))
            files = json.loads(s.makefile("r", encoding="utf-8").readline())
    # caso esteja desligado
    except FileNotFoundError, ConnectionRefusedError:
        print("\033[2;m[ tot desligado, ligue com 'tot system daemon' ]\033[0;0m")
        files = scan()["files"]
    # retorna o files de qualquer jeito
    return files

def get_metrics():
    files = get_files()

    backlinks = Counter(l for d in files.values() for l in set(d["links"]))
    tags = Counter(t for d in files.values() for t in set(d["tags"]))

    print(30*"-")
    print(f"notas existentes:    \033[1;92m{len(files)}\033[0;0m")
    print(f"tags existentes:     \033[1;92m{len(tags)}\033[0;0m")
    print(f"links feitos:        \033[1;92m{sum(len(d['links']) for d in files.values())}\033[0;0m")
    print("\ntop notas mais linkadas:")
    for nota, n in backlinks.most_common(5):
        print(f"{n}    \033[1;36m{nota}\033[0;0m")
    print("\ntop tags mais usadas:")
    for tag, n in tags.most_common(5):
        print(f"{n}    \033[1;34m@{tag}\033[0;0m")
    orfas = [n for n, d in files.items() if not d["links"] and n not in backlinks]
    print(f"\nnotas não linkadas:  \033[1;33m{len(orfas)}\033[0;0m")
    quebrados = [(n, l) for n, d in files.items() for l in d["links"] if l not in files]
    print(f"\nlinks quebrados:     \033[1;31m{len(quebrados)}\033[0;0m")
    print(30*"-")

def find_tag(tag: str):
    files = get_files()
    tag = tag.lstrip("@")
    notas = sorted(n for n, d in files.items() if tag in d["tags"])

    print(30*"-")
    if not notas:
        print(f"nenhuma nota com a tag '{tag}'")
        return

    print(f"{len(notas)} nota(s) com a tag '{tag}':")
    for nota in notas:
        print(f"  {nota}")
    print(30*"-")


def find_note(busca: str):
    files = get_files()
    busca = busca.lower()
    achadas = sorted(n for n in files if busca in n.lower())

    exatas = [n for n in achadas if n.lower() == busca]
    if exatas:
        achadas = exatas

    print(30*"-")
    if not achadas:
        print(f"nenhuma nota encontrada com '{busca}'")
        return
    if len(achadas) > 1:
        print("várias notas encontradas")
        for n in achadas:
            print(f"  {n}")
        return

    nota = achadas[0]
    dados = files[nota]
    backlinks = sorted(n for n, d in files.items() if nota in d["links"])

    print(nota)
    print(f"tags: {', '.join(dados['tags']) or '-'}")

    print(f"\nlinka pra ({len(dados['links'])}):")
    for link in dados["links"]:
        print(f"  {link}")

    print(f"\nlinkada por ({len(backlinks)}):")
    for n in backlinks:
        print(f"  {n}")
    print(30*"-")
