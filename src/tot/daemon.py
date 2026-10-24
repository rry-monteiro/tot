from pathlib import Path

from watchfiles import Change, watch

from . import core

"""
--- exemple watchfiles--- 
# <<<
{(<Change.added: 1>, '/home/rry/Documentos/notas.tot/teste')}
{(<Change.added: 1>, '/home/rry/Documentos/notas.tot/teste_mudança de nome'), (<Change.deleted: 3>, '/home/rry/Documentos/notas.tot/teste')}
{(<Change.deleted: 3>, '/home/rry/Documentos/notas.tot/teste_mudança de nome')}
{(<Change.modified: 2>, '/home/rry/Documentos/notas.tot/wpa_supplicant.md')}


1. added -> parsear o arquivo e serializar os resultados
2. added+deleted (mudança de nome) -> altero o nome do arquivo na serialização e nas notas do user
3. deleted -> removo o nó e as arestas da serialização, removo os links que o user fez no vault (deixando nota de arquivo deletado)
4. modified -> parsear o arquivo e serializar resultados (caso mudem)
# >>>
--- exemple watchfiles--- 

--- exemple js ---
# <<<
const GRAFOS = {
  tags: { 
    nodes: [
      { id: "python", kind: "tag" },
      { id: "linux", kind: "tag" },
      { id: "api.md", kind: "note" },
      { id: "models.md", kind: "note" },
      { id: "terminal.md", kind: "note" }
    ], 
    links: [
      { source: "python", target: "api.md" },
      { source: "python", target: "models.md" },
      { source: "linux", target: "terminal.md" },
      { source: "linux", target: "api.md" }
    ] 
  },
  links: { 
    nodes: [
      { id: "api.md", kind: "note" },
      { id: "models.md", kind: "note" },
      { id: "terminal.md", kind: "note" }
    ], 
    links: [
      { source: "api.md", target: "models.md" },
      { source: "terminal.md", target: "api.md" }
    ] 
  }
};
# >>>
--- exemple js ---

--- obs ---
os ids são os caminhos relativos ao path
--- obs ---
"""


def run():
    assert core.VAULT is not None
    vault = core.VAULT
    files = core.scan()["files"]

    def rel(p) -> str:
        return str(Path(p).relative_to(vault))

    for mud in watch(vault, watch_filter=lambda _, p: p.lower().endswith(".md")):
        # capturando deleções e adições do vault
        deleted = [p for t, p in mud if t == Change.deleted]
        added = [p for t, p in mud if t == Change.added]

        # se os dois existirem na mesma "linha"
        if len(deleted) == 1 and len(added) == 1:
            # captura o antigo (detelado) e o novo (adicinado)
            old, new = rel(deleted[0]), rel(added[0])
            # se o antigo existe no vault serializado e o hash dos dois é igual
                # movimentação de arquivo
            if old in files and core.hash_is_equal(files, old, added[0]):
                # parseia o arquivo
                files[new] = core.parser(Path(added[0]))[1]
                # remove o antigo
                del files[old]
                # transforma tudo em novo
                for info in files.values():
                    info["links"] = [new if l == old else l for l in info["links"]]
                # proxima mudança
                continue

        for tipo, arquivo in mud:
            if tipo in (Change.added, Change.modified):
                try:
                    chave, info = core.parser(Path(arquivo))
                except FileNotFoundError:
                    continue
                files[chave] = info
            elif tipo == Change.deleted:
                files.pop(rel(arquivo), None)

        for arquivo, dados in files.items():
            print(arquivo, "=", dados["links"], dados["tags"])
