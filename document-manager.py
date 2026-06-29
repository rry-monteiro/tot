from pathlib import Path
from hashlib import blake2b
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
        return list(Path(self.path_vault).rglob("*.md"))

    # captura todos os atributos necessários pra preencher o json
    def _get_all_note_attribute(self, path_note:Path)->dict:
        return

    # pega o hash de um arquivo
    def _get_hash(self, path_note:Path)->str:
        h = blake2b()
        with open(path_note, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
        
    # compara o hash atual com o hash do json
    def _hash_is_equal(self, path_note:Path):
        hash_atual = self._get_hash(path_note)
        hash_json = self.data["arquivos"][str(path_note)]["hash"]

        return True if hash_atual == hash_json else False


    # compara o mtime atual com o do json
    def _mtime_is_equal(self, path_note:Path)->bool:
        mtime_atual = path_note.stat().st_mtime
        mtime_json = self.data["arquivos"][str(path_note)]["mtime"]

        return True if mtime_atual == mtime_json else False

    # ajusta o json de acordo com as mudanças (ou não)
    def run(self):
        # capturo todas as notas do treco
        notes = self._get_notes()

        # itero nas notas
        for n in notes:
            
            # verifico a existencia no json
            if n.relative_to(self.path_vault) in self.data["arquivos"].keys():
                """ARQUIVO EXISTENTE, VERIFICA ALTERAÇÃO"""
                # se ele existe, verifica o mtime e compara
                if self._mtime_is_equal(n):
                    """ARQUIVO INTACTO"""
                else:
                    """POSSIVEL MUDANÇA NO HASH"""
                    # se mudou o mtime, temos certeza validando o hash
                    if self._hash_is_equal(n):
                        """ARQUIVO REALMENTE INTACTO"""
                    else:
                        """ARQUIVO MUDOU, TRATA PARSEANDO TUDO"""
                        pass
            else:
                """ARQUIVO NOVO, TRATA"""
                pass
                
                




