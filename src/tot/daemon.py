from pathlib import Path

from watchfiles import watch

"""
--- exemple --- 
{(<Change.added: 1>, '/home/rry/Documentos/notas.tot/teste')}
{(<Change.added: 1>, '/home/rry/Documentos/notas.tot/teste_mudança de nome'), (<Change.deleted: 3>, '/home/rry/Documentos/notas.tot/teste')}
{(<Change.deleted: 3>, '/home/rry/Documentos/notas.tot/teste_mudança de nome')}
{(<Change.modified: 2>, '/home/rry/Documentos/notas.tot/wpa_supplicant.md')}
--- exemple --- 
"""


def run(vault: Path):
    for mud in watch(vault):
        print(mud)
