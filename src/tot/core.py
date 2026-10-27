import hashlib
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from platformdirs import user_documents_dir

VAULT: Path | None = None
REGEX_TAGS = re.compile(r"tags:\s*\[([^\]]*)\]")
REGEX_LINKS = re.compile(r'\[[^\]]+\]\(([^)#\s"]+\.md)')


class Vault:
    def __init__(self, files: dict, vault: Path):
        self.files = files
        self.vault = vault

    def replace_refs(self, old:str, new:str):
        for dados in self.files.values(): # pra cada dado nos valores
            # itera em tudo mudando os valores pro nome novo
            dados["links"] = [
                new if link == old else link
                for link in dados["links"]
            ]

    def update(self, arquivo:str):
        chave, info = parser(Path(arquivo))  # parseia o aarquivo
        self.files[chave] = info  # guarda as informações

    def delete(self, arquivo):
        chave = str(Path(arquivo).relative_to(self.vault)) # encontra o str do path relativo da nota
        self.files.pop(chave, None) # remove dos arquivos


    def move(self, origem:str, destino:str):
        old = str(Path(origem).relative_to(self.vault)) # captura o antigo relativo (chave)
        new = str(Path(destino).relative_to(self.vault)) # captura o novo relativo (chave nova)

        if old not in self.files: # se o nome antigo não ta indexado
            self.update(destino) # indexa com o nome novo
            return # retorna daqui mesmo

        info = self.files.pop(old) # remove o antigo e pega os dados
        self.files[new] = info # adicona o nome novo com os mesmos dados

        # atualização das referências
        self.replace_refs(old, new)

    def move_dir(self, origem:str, destino:str):
        old = str(Path(origem).relative_to(self.vault))
        new = str(Path(destino).relative_to(self.vault))

        def replace(caminho):
            if caminho == old:  # se o caminho for igual o antigo
                return new     # retorna o novo

            if caminho.startswith(old + "/"): # se o caminho começa com o nome antigo + /
                return new + caminho[len(old):] # retorna nome_novo/nome_do_arquiv, len(old) corta o nome antigo
            return caminho

        # substituimos tudo
        self.files = {
            replace(chave): info
            for chave, info in self.files.items()
        }
        
        # atualizamos as referências
        self.replace_refs(old, new)

    def add_dir(self):...

    def delete_dir(self): ...

        







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
