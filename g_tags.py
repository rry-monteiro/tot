from pathlib import Path
import json
from nethtml import HTML_TEMPLATE

class TagsGraphGenerator():
    def __init__(self, path_output:Path, path_data:Path, path_vault:Path):
        self.path_output = path_output
        self.data = json.loads(path_data.read_text())
        self.path_vault = Path(path_vault)

    def _build(self):
        # salvo os arquivos
        arquivos = self.data["arquivos"]
        # defino a lsiat de nodes para notas
        nodes = []
        edges = []
        tag_nodes = {} #ponteiro

        # central
        nodes.append({
            "id": "__center__",
            "shape": "dot",
            "size": 0,
            "mass": 30,
            "fixed": True,
            "x": 0,
            "y": 0
        })

        # nodes
        # loop nos dados
        for note, dados in arquivos.items():
            # pra cada arquivo, crio um node
            nodes.append({
                "color": {
                    "background": "#24282b",
                    "border": "#565f89",
                    "highlight": {"background": "#414868", "border": "#7aa2f7"}
                },
                "font": {"color": "#c0caf5", "size":15},
                "id": note,
                "label": note, #nome do arquivo como nome do nó
                "shape": "circle",
                "title" : note
            })
            # pra cada tag em cada arquivo
            for tag in dados["tags"]:
                # define o id
                tag_id = f"@{tag}"
                # adiciona o edge ARQUIVO -> TAG
                edges.append({
                    "color": {
                        "color": "#565f89",
                        "highlight": "#7dcfff",
                        "hover": "#7aa2f7",
                        "opacity": 0.6
                    },
                    "font": {"color": "#a9b1d6", "size": 12},
                    "from": note,
                    "to": tag_id,
                    "width": 6,
                })
                # se não passamos pela tag ainda, ela é nova, adiciona no ponteiro
                if tag not in tag_nodes:
                    # cria o ponteiro de nodes
                    tag_nodes[tag] = {
                        "color": {"background": "#7aa2f7"},
                        "font": {"color": "#c0caf5", "size": 5},
                        "id": tag_id,
                        "label": tag_id,
                        "shape": "dot",
                        "title": tag_id,
                        "value": 1,
                        "mass": 10
                    }
                    # adiciona nos nodes
                    nodes.append(tag_nodes[tag])

                    #cria o edge TAG -> CENTRO
                    edges.append({
                        "from": "__center__",
                        "to": tag_id,
                        "width": 10,
                        "color": {
                            "color": "#565f89",
                            "highlight": "#7dcfff",
                            "hover": "#7aa2f7",
                            "opacity": 0.7
                        },
                    })
                # se ja passamos por ela, aumenta seu valor no ponteiro
                else:
                    tag_nodes[tag]["value"] += 1.5
                    tag_nodes[tag]["font"]["size"] = tag_nodes[tag]["value"] * 5

        # retorna as listas
        return nodes, edges

    def render(self):
        nodes, edges = self._build()
        html = HTML_TEMPLATE.replace("## NODES ##", json.dumps(nodes))
        html = html.replace("## EDGES ##", json.dumps(edges))
        self.path_output.write_text(html, encoding="utf-8")
