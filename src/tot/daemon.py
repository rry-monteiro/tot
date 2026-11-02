import json
import socket
import threading
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.utils.event_debouncer import EventDebouncer

from . import core, vault_index

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

SOCK = core.SOCK
LOCK = threading.Lock()


class Manager(FileSystemEventHandler):
    def __init__(self, debouncer):
        self.debouncer = debouncer

    def on_any_event(self, event):
        self.debouncer.handle_event(event)


def processar(events, indice):
    fila: dict[str, tuple | str] = {}

    for event in events:
        # <<<
        match event.event_type:
            case "created" | "modified":
                if event.is_directory:
                    if event.event_type == "created":
                        fila[event.src_path] = "update_dir"
                elif event.src_path.endswith(".md"):
                    fila[event.src_path] = "update"

            case "deleted":
                if not event.is_directory:
                    fila[event.src_path] = "delete"
                else:
                    fila[event.src_path] = "delete_dir"

            case "moved":
                if not event.is_directory:
                    fila[event.src_path] = ("move", event.dest_path)
                else:
                    fila[event.src_path] = ("move_dir", event.dest_path)
        # >>>

    for caminho, operacao in fila.items():
        # <<<
        match operacao:
            case "update":
                indice.update(caminho)
            case "delete":
                indice.delete(caminho)
            case ("move", destino):
                indice.move(caminho, destino)
            case "update_dir":
                indice.update_dir(caminho)
            case "delete_dir":
                indice.delete_dir(caminho)
            case ("move_dir", destino):
                indice.move_dir(caminho, destino)
        # >>>
    if fila:
        data = indice.build_js()
        core.build_graph(data)


def servir(indice):
    """thread principal"""
    SOCK.parent.mkdir(parents=True, exist_ok=True)
    SOCK.unlink(missing_ok=True)  # sobra de um daemon que morreu
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as srv:
        srv.bind(str(core.SOCK))
        srv.listen()
        while True:
            conn, _ = srv.accept()  # bloqueia até alguém conectar
            with conn:
                try:
                    with LOCK:  # segura só enquanto serializa
                        msg = json.dumps(indice.files, ensure_ascii=False) + "\n"
                    conn.sendall(msg.encode("utf-8"))
                except OSError:
                    pass  # cliente desconectou no meio


def run():
    assert core.VAULT is not None

    vault: Path = core.VAULT  # o vault, Path
    files: dict = core.scan()["files"]  # serialização dos dados do vault

    # define o vaultIndex
    indice = vault_index.VaultIndex(files, vault)

    # inicia coinstruindo o grafico
    data = indice.build_js()
    core.build_graph(data)

    # define o deboucer
    debouncer = EventDebouncer(
        debounce_interval_seconds=1,
        events_callback=lambda events: processar(events, indice),
    )
    manager = Manager(debouncer)  # dispara os eventos
    observer = Observer()  # observa
    observer.schedule(
        event_handler=manager, path=str(vault), recursive=True
    )  # liga um ao outro
    observer.start()
    debouncer.start()

    try:
        servir(indice)  # thread principal fica aqui, no lugar do join()
    finally:
        observer.stop()
        debouncer.stop()
        SOCK.unlink(missing_ok=True)
