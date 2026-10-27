from pathlib import Path

from . import core


class VaultIndex:
    def __init__(self, files: dict, vault: Path):
        self.files = files
        self.vault = vault

    def replace_refs(self, old: str, new: str):
        """
        substitui todas as referências dos dados das notas, itera em tudo e troca pelo nome novo
        """
        for dados in self.files.values():  # pra cada dado nos valores
            # itera em tudo mudando os valores pro nome novo
            dados["links"] = [new if link == old else link for link in dados["links"]]

    def update(self, arquivo: str):
        """
        parseia o arquivo e adicona nos dados
        """
        chave, info = core.parser(Path(arquivo))  # parseia o aarquivo
        self.files[chave] = info  # guarda as informações

    def delete(self, arquivo):
        """
        remove um arquivo e seus dados do vault
        """
        chave = str(Path(arquivo).relative_to(self.vault))  # encontra o str do path relativo da nota
        self.files.pop(chave, None)  # remove dos arquivos

    def move(self, origem: str, destino: str):
        """
        muda o nome do dado no vault apagando o nome antigo e adiconando o novo,
        caso o antigo não exista, faz update
        """
        old = str(Path(origem).relative_to(self.vault))  # captura o antigo relativo (chave)
        new = str(Path(destino).relative_to(self.vault))  # captura o novo relativo (chave nova)

        if old not in self.files:  # se o nome antigo não ta indexado
            self.update(destino)  # indexa com o nome novo
            return  # retorna daqui mesmo

        info = self.files.pop(old)  # remove o antigo e pega os dados
        self.files[new] = info  # adicona o nome novo com os mesmos dados

        # atualização das referências
        self.replace_refs(old, new)

    def move_dir(self, origem: str, destino: str):
        """
        substitui as chaves que chamam um arquivo dentro de pasta, treocando o
        nome da pasta antiga pelo nome que ela recebeu
        """
        old = str(Path(origem).relative_to(self.vault))
        new = str(Path(destino).relative_to(self.vault))

        def replace(caminho):
            if caminho == old:  # se o caminho for igual o antigo
                return new  # retorna o novo

            if caminho.startswith(
                old + "/"
            ):  # se o caminho começa com o nome antigo + /
                return (
                    new + caminho[len(old) :]
                )  # retorna nome_novo/nome_do_arquiv, len(old) corta o nome antigo
            return caminho

        # substituimos tudo
        self.files = {replace(chave): info for chave, info in self.files.items()}

        # atualizamos as referências
        self.replace_refs(old, new)

    def update_dir(self):
        """
        adiciona todos os arquivos de uma pasta nova em files, fazendo um for(update) em tudo
        """

    def delete_dir(self):
        """
        remove todos os arquivos da serialização quando uma pasta é deletada fazendor for(delete) em tudo
        """
