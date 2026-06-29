from pathlib import Path
from hashlib import blake2b
import json
import re

class DocumentManager():
    def __init__(self, path_output:Path, path_vault:Path, output_name:str, path_data:Path):
        # <<<
        # saída e entrada de dados
        self.path_output = Path(path_output) / f"{output_name}.html"
        self.path_vault = Path(path_vault)
        self.path_vault.mkdir(parents=True, exist_ok=True)
        self.path_output.mkdir(parents=True, exist_ok=True)

        #capturando estado do json
        self.path_data = Path(path_data)
        if self.path_data.exists():
            self.data = json.loads(self.path_data.read_text())
        else:
            self.data = {"arquivos": {}}

        # compilando padrões de regex
        self.RE_TAGS = re.compile(r"tags:\s*\[([^\]]*)\]")
        self.RE_LINKS = re.compile(r'\[[^\]]+\]\(([^)#\s"]+\.md)')

        # flag de mudanças
        self.has_changes=False
        self.has_only_json_changes=False
        # >>>

    # captura a lista de todas as notas no vault
    def _get_notes(self)->list:
        return list(Path(self.path_vault).rglob("*.md"))

    # pega o hash de um arquivo
    def _get_hash(self, path_note:Path)->str:
        h = blake2b(digest_size=32)
        with open(path_note, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
        
    # compara o hash atual com o hash do json
    def _hash_is_equal(self, path_note:Path)->bool:
        hash_atual = self._get_hash(path_note)
        hash_json = self.data["arquivos"][str(path_note.relative_to(self.path_vault))]["hash"]

        return True if hash_atual == hash_json else False

    # compara o mtime atual com o do json
    def _mtime_is_equal(self, path_note:Path)->bool:
        mtime_atual = path_note.stat().st_mtime
        mtime_json = self.data["arquivos"][str(path_note.relative_to(self.path_vault))]["mtime"]

        return True if mtime_atual == mtime_json else False

    def _update_mtime(self, path_note:Path)->None:
        mtime_novo = path_note.stat().st_mtime
        self.data["arquivos"][str(path_note.relative_to(self.path_vault))]["mtime"] = mtime_novo
        
    #resolve os paths dos links
    def _resolve_links_path(self, links_brutos:list, path_note:Path)->list:
        # <<<
        dir_note = path_note.parent
        links = []

        for lk in links_brutos:
            absolute_path = (dir_note / lk).resolve()
            relative_path = absolute_path.relative_to(self.path_vault)
            links.append(str(relative_path))
        # >>>
        return links

    # pega todos os links e tags do documento
    def _get_links_and_tags(self, path_note:Path)->tuple:
        # <<<
        # pega o conteúdo da nota
        conteudo = path_note.read_text(encoding="utf-8")

        # devolve uma lista de strings não prontas
        m_tags = self.RE_TAGS.findall(conteudo)
        tags = [t.strip() for grupo in m_tags for t in grupo.split(",") if t.strip()]

        # devolve uma lista de tuplas com [] e ()
        m_links = self.RE_LINKS.findall(conteudo)
        links = self._resolve_links_path(m_links, path_note)
        # >>>
        return tags, links

    # processa um arquivo quando é alterado
    def _process_file(self, path_note:Path)->None:
        # <<<
        new_hash = self._get_hash(path_note)
        new_mtime = path_note.stat().st_mtime
        tags, links = self._get_links_and_tags(path_note)
        
        self.data["arquivos"][str(path_note.relative_to(self.path_vault))] = \
        {
            "mtime" : new_mtime,
            "hash" : new_hash,
            "tags" : tags,
            "links": links
        }
        # >>>

    # ajusta o json de acordo com as mudanças (ou não)
    def run(self):
        # <<<
        # capturo todas as notas do treco
        notes = self._get_notes()
        notes_set = {str(n) for n in notes}  # pra deleção ser O(1)

        # deleto as notas apagadas
        for note in list(self.data["arquivos"].keys()):
            if str(self.path_vault / note) not in notes_set:
                del self.data["arquivos"][note]
                self.has_changes = True

        # itero nas notas
        for n in notes:
            # verifico a existencia no json
            if n.relative_to(self.path_vault) in list(self.data["arquivos"].keys()):
                """ARQUIVO EXISTENTE, VERIFICA ALTERAÇÃO"""
                # se ele existe, verifica o mtime e compara
                if self._mtime_is_equal(n):
                    """ARQUIVO INTACTO"""
                    continue
                else:
                    """POSSIVEL MUDANÇA NO HASH"""
                    # se mudou o mtime, temos certeza validando o hash
                    if self._hash_is_equal(n):
                        """ARQUIVO REALMENTE INTACTO, ATUALIZA SÓ O MTIME NA MEMORIA"""
                        self._update_mtime(n)
                    else:
                        """ARQUIVO MUDOU, TRATA PARSEANDO TUDO E JOGA NA MEMORIA"""
                        self._process_file(n)
                        self.has_changes=True
            else:
                """ARQUIVO NOVO, TRATA"""
                self._process_file(n)
                self.has_changes=True

        self.path_data.write_text(
            json.dumps(self.data, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )

        # >>>
        return self.has_changes
