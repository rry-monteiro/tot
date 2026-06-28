from pathlib import Path
from hashlib import sha256
import json
import re

class DocumentManager():
    def __init__(self, path_output:Path, path_vault:Path, output_name:str, path_data:Path):
        # <<<
        # saída e entrada de dados
        self.path_output = path_output / output_name+".html"
        self.path_vault = path_vault
        self.path_vault.mkdir(parents=True, exist_ok=True)
        self.path_output.mkdir(parents=True, exist_ok=True)

        #capturando estado do json
        self.path_data = path_data
        self.data = json.loads(self.path_data.read_text())

        # compilando padrões de regex
        self.RE_TAGS = re.compile(r"tags:\s*\[([^\]]*)\]")
        self.RE_LINKS = None #depois adiciona
        # >>>

    # captura a lista de todas as notas no vault
    def _get_notes(self)->list:
        return list(Path(self.path_vault).rglob("*"))

    # captura todos os atributos necessários pra preencher o json
    def _get_all_note_attribute(self, path_note:Path)->dict:
        return
