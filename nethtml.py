HTML_TEMPLATE = \
"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/dist/vis-network.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/vis-network.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <style>
        body { margin: 0; }
        #mynetwork {
            width: 100%;
            height: 100vh;
            background-color: #1a1b26;
        }
    </style>
</head>
<body>
    <div id="mynetwork"></div>
    <script>
        var nodes = new vis.DataSet(## NODES ##);
        var edges = new vis.DataSet(## EDGES ##);
        var container = document.getElementById('mynetwork');
        var options = {
            "nodes": {
                "scaling": {
                    "min": 40,
                    "max": 220
                }
            },
            "edges": {
                "smooth": {
                    "enabled": false
                },
                "selectionWidth": 3,
                "hoverWidth": 3
            },
            "physics": {
                "enabled": true,
                "solver": "forceAtlas2Based",
                "forceAtlas2Based": {
                    "gravitationalConstant": -571,
                    "centralGravity": 0.01,
                    "springLength": 300,
                    "springConstant": 0.02,
                    "damping": 0.999999,
                    "avoidOverlap": 1.0
                },
                "maxVelocity": 30,
                "minVelocity": 1,
                "stabilization": {
                    "enabled": true,
                    "iterations": 2000,
                    "updateInterval": 25
                }
            },
            "interaction": {
                "hover": false,
                "hoverConnectedEdges": false,
                "selectConnectedEdges": true,
                "dragNodes": true,
                "dragView": true,
                "zoomView": true,
                "tooltipDelay": 200
            }
        };
        new vis.Network(container, { nodes: nodes, edges: edges }, options);
    </script>
</body>
</html>
"""


