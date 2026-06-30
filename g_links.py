from pathlib import Path
import json
from nethtml import HTML_TEMPLATE

class LinksGraphGenerator():
    def __init__(self, path_output:Path, path_data:Path, path_vault:Path):
        self.path_output = path_output
        self.data = json.loads(path_data.read_text())
        self.path_vault = Path(path_vault)

    def _build(self):
        # <<<
        #arquivos
        arquivos = self.data["arquivos"]
        nodes = []
        edges = []

        # central pra ggravidade apenas
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
        for note, dados in arquivos.items():
            # pra cada arquivo, crio um node
            nodes.append({
                "color": {
                    "background": "#24282b",
                    "border": "#565f89",
                    "highlight": {"background": "#414868", "border": "#7aa2f7"}
                },
                "font": {"color": "#c0caf5", "size":35},
                "id": note,
                "label": note,
                "shape": "box",
                "widthConstraint" : 250,
                "heightConstraint" : 250,
                "title" : note,
                "mass" : len(dados["links"])*1.5
            })

            # itero nos liks de cada um (ja que os links são nodes)
            for node_link in dados["links"]:
                print(node_link)
                edges.append({
                    "color": {
                        "color": "#565f89",
                        "highlight": "#7dcfff",
                        "hover": "#7aa2f7",
                        "opacity": 1
                    },
                    "font": {"color": "#a9b1d6", "size": 12},
                    "from": note,
                    "to": node_link,
                    "arrows": {"to": {"enabled":True, "scaleFactor": 4, "type":"circle"} },
                    "width": 5,
                })
        # >>>
        return nodes, edges

    def render(self):
        nodes, edges = self._build()
        html = HTML_TEMPLATE.replace("## NODES ##", json.dumps(nodes))
        html = html.replace("## EDGES ##", json.dumps(edges))
        self.path_output.write_text(html, encoding="utf-8")
