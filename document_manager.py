from pathlib import Path
from hashlib import blake2b
import json
import re

class DocumentManager():
    def __init__(self, path_data:Path, path_vault:Path):
        # <<<
        # saída e entrada de dados
        self.path_vault = path_vault
        self.path_vault.mkdir(parents=True, exist_ok=True)

        #capturando estado do json
        self.path_data = path_data
        if self.path_data.exists():
            self.data = json.loads(self.path_data.read_text())
        else:
            self.data = {"arquivos": {}}

        # compilando padrões de regex
        self.RE_TAGS = re.compile(r"tags:\s*\[([^\]]*)\]")
        self.RE_LINKS = re.compile(r'\[[^\]]+\]\(([^)#\s"]+\.md)')

        # flag de mudanças
        self.has_changes=False
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
        new_inode = f"{path_note.stat().st_dev}:{path_note.stat().st_ino}"
        tags, links = self._get_links_and_tags(path_note)
        
        self.data["arquivos"][str(path_note.relative_to(self.path_vault))] = \
        {
            "mtime" : new_mtime,
            "hash" : new_hash,
            "inode": new_inode,
            "tags" : tags,
            "links": links
        }
        # >>>

    def run(self):
        # todas as notas em path
        notes = self._get_notes()
        # mapeia inode -> path pelo vault pra deleção e detctar mudança de path
        map_inode_vault = {f"{note.stat().st_dev}:{note.stat().st_ino}" : str(note.relative_to(self.path_vault)) for note in notes}
        # mapeia o redirecionamento: antigo -> novo pra editar o "arquivos" depois

        # itero no json
        for n in list(self.data["arquivos"].keys()):
            # verifico se o inode do existe no map
            inode = self.data["arquivos"][n]["inode"]
            
            if inode not in map_inode_vault:
                # ta no json mas não ta n vault = DELETADO
                del self.data["arquivos"][n]
                self.has_changes = True
                
            elif map_inode_vault[inode] != n:
                # nome do map não é o mesmo nome do json = MOVIDO
                novo_path = map_inode_vault[inode]
                # puxo tudo do original
                self.data["arquivos"][novo_path] = self.data["arquivos"][n]
                # deleto o original
                del self.data["arquivos"][n]

        # iterando nas notas do vault
        for n in notes:
            # verificando existencia no json:
            if str(n.relative_to(self.path_vault)) not in list(self.data["arquivos"].keys()):
                # não existe, é novo:
                self._process_file(n)
                self.has_changes = True
            else:
                # existe, verifica alterações por blocos
                # MTIME
                if self._mtime_is_equal(n):
                    # mtime nomral, pula
                    continue
                else:
                    #mtime diferente, bloco 2
                    # HASH
                    if self._hash_is_equal(n):
                        # hash ta igual, atualiza só o mtime
                        self._update_mtime(n)
                    else:
                        # hash mudou, parseia o arquivo
                        self._process_file(n)
                        self.has_changes = True

        # salva o treco
        # indentação atrasa mas é pra ficar legivel
        self.path_data.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        return self.has_changes
