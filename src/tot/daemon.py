from watchdog.events import FileSystemEventHandler

from watchdog.utils.event_debouncer import EventDebouncer
from watchdog.observers import Observer

from . import core

"""
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

--- exemplo watchdog ---
# <<<
created /home/rry/Documentos/notas.tot/asdfasdf
modified /home/rry/Documentos/notas.tot
opened /home/rry/Documentos/notas.tot/asdfasdf
closed /home/rry/Documentos/notas.tot/asdfasdf
modified /home/rry/Documentos/notas.tot
opened /home/rry/Documentos/notas.tot/asdfasdf
closed_no_write /home/rry/Documentos/notas.tot/asdfasdf
moved /home/rry/Documentos/notas.tot/asdfasdf
modified /home/rry/Documentos/notas.tot
opened /home/rry/Documentos/notas.tot/asdfasdfaskjdfhgaskdjhf
closed_no_write /home/rry/Documentos/notas.tot/asdfasdfaskjdfhgaskdjhf
opened /home/rry/Documentos/notas.tot/asdfasdfaskjdfhgaskdjhf
closed_no_write /home/rry/Documentos/notas.tot/asdfasdfaskjdfhgaskdjhf
deleted /home/rry/Documentos/notas.tot/asdfasdfaskjdfhgaskdjhf
modified /home/rry/Documentos/notas.tot
# >>>
--- exemplo watchdog ---

--- obs ---
os ids são os caminhos relativos ao path
--- obs ---
"""


class Manager(FileSystemEventHandler):
    def __init__(self, debouncer):
        self.debouncer = debouncer

    def on_any_event(self, event):
        self.debouncer.handle_event(event)


def processar(events):
    for event in events:
        print(event.event_type, event.src_path)


def run():
    assert core.VAULT is not None
    vault = core.VAULT
    files = core.scan()["files"]

    debouncer = EventDebouncer(debounce_interval_seconds=1, events_callback=processar)
    manager = Manager(debouncer)  # dispara os eventos
    observer = Observer()  # observa
    observer.schedule(
        event_handler=manager, path=str(vault), recursive=True
    )  # liga um ao outro
    observer.start()
    debouncer.start()
    observer.join()
    debouncer.join()

    # for mud in watch(vault, watch_filter=lambda _, p: p.lower().endswith(".md")):
    #     # capturando deleções e adições do vault
    #     deleted = [p for t, p in mud if t == Change.deleted]
    #     added = [p for t, p in mud if t == Change.added]
    #
    #     # se os dois existirem na mesma "linha"
    #     if len(deleted) == 1 and len(added) == 1:
    #         # captura o antigo (detelado) e o novo (adicinado)
    #         old, new = rel(deleted[0]), rel(added[0])
    #         # se o antigo existe no vault serializado e o hash dos dois é igual
    #             # movimentação de arquivo
    #         if old in files and core.hash_is_equal(files, old, added[0]):
    #             # parseia o arquivo
    #             files[new] = core.parser(Path(added[0]))[1]
    #             # remove o antigo
    #             del files[old]
    #             # transforma tudo em novo
    #             for info in files.values():
    #                 info["links"] = [new if l == old else l for l in info["links"]]
    #             # proxima mudança
    #             continue
    #
    #     for tipo, arquivo in mud:
    #         if tipo in (Change.added, Change.modified):
    #             try:
    #                 chave, info = core.parser(Path(arquivo))
    #             except FileNotFoundError:
    #                 continue
    #             files[chave] = info
    #         elif tipo == Change.deleted:
    #             files.pop(rel(arquivo), None)
    #
    #     for arquivo, dados in files.items():
    #         print(arquivo, "=", dados["links"], dados["tags"])
