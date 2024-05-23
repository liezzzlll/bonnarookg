import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import networkx as nx
from collections import Counter
from pyvis.network import Network
from IPython.core.display import display, HTML

# Load your dataset
data = pd.read_csv("Bonnaroo_KG.csv")

# Create a Streamlit title
st.title('2024 Bonnaroo Music Festival Knowledge Graph')

# Add a map key for colors and shapes
st.markdown("""
## Map Key

**Node Colors & Shape:**
- `Artist`: <span style="color:#e07c3e;">Orange</span> ellipse
- `Genre`: <span style="color:#1f77b4;">Blue</span> star - size is scaled based on how many artists fall under that genre.
- `Set Day`: <span style="color:#2ca02c;">Green</span> dot
- `Roo Location`: <span style="color:#9467bd;">Purple</span> triangle
- `Stage Name`: <span style="color:#8c564b;">Brown</span> square

""", unsafe_allow_html=True)

# Shape map defined
shape_map = {
    'Artist': 'ellipse',
    'Genre': 'star',
    'Set Day': 'dot',
    'Roo Location': 'triangle',
    'Stage Name': 'square',
}

# Color map defined
color_map = {
    'Artist': '#e07c3e',
    'Genre': '#1f77b4',
    'Set Day': '#2ca02c',
    'Roo Location': '#9467bd',
    'Stage Name': '#8c564b',
}

def create_knowledge_graph(data):
    net = Network(notebook=False, height="750px", width="100%", bgcolor="#222222", font_color="white", select_menu=True, filter_menu=False)

    # Count the number of artists per genre
    genre_counts = Counter()
    for genres in data['Genre'].str.split(','):
        genre_counts.update([genre.strip() for genre in genres])

    # Ensure each node is only added once, maintain a set of nodes    
    added_nodes = set()

    # Add nodes and edges for each row in the dataframe
    for index, row in data.iterrows():
        artist_node = str(row['Artist'])
        genres = row['Genre'].split(',')
        day_node = str(row['Set Day'])
        stage_node = str(row['Stage Name'])
        location_node = str(row['Roo Location'])

        # Add artist node
        if artist_node not in added_nodes:
            net.add_node(artist_node, title=artist_node, color="#ffcc00")
            added_nodes.add(artist_node)
        
        # Add genre nodes and edges
        for genre in genres:
            genre_node = genre.strip()
            genre_size = genre_counts[genre_node] * 10  # Adjust the multiplier for size scaling
            if genre_node not in added_nodes:
                net.add_node(genre_node, title=genre_node, color=color_map['Genre'], shape=shape_map['Genre'], size=genre_size)
                added_nodes.add(genre_node)
            net.add_edge(artist_node, genre_node)

        # Add set day node and edges
        if day_node not in added_nodes:
            net.add_node(day_node, title=day_node, color=color_map['Set Day'], shape=shape_map['Set Day'])
            added_nodes.add(day_node)
        net.add_edge(artist_node, day_node)

        # Add stage name node and edges
        if stage_node not in added_nodes:
            net.add_node(stage_node, title=stage_node, color=color_map['Stage Name'], shape=shape_map['Stage Name'])
            added_nodes.add(stage_node)
        net.add_edge(artist_node, stage_node)

        # Add location node and edges
        if location_node not in added_nodes:
            net.add_node(location_node, title=location_node, color=color_map['Roo Location'], shape=shape_map['Roo Location'])
            added_nodes.add(location_node)
        net.add_edge(artist_node, location_node)

    # Configure physics and interaction options
    net.set_options("""
    {
      "nodes": {
        "borderWidth": 2,
        "size": 30,
        "color": {
          "border": "#222222",
          "background": "#666666"
        },
        "font": { "color": "#eeeeee" }
      },
      "edges": {
        "color": "lightgray"
      },
      "physics": {
        "enabled": true,
        "stabilization": {
          "enabled": true,
          "iterations": 200,
          "updateInterval": 25
        },
        "barnesHut": {
          "gravitationalConstant": -20000,
          "centralGravity": 0.3,
          "springLength": 95,
          "springConstant": 0.04,
          "damping": 0.09
        }
      },
      "interaction": {
        "navigationButtons": true,
        "keyboard": true
      }
    }
    """)

    net.save_graph('bonnaroo.html')

    # Load the generated HTML file
    with open('bonnaroo.html', 'r') as file:
        html_content = file.read()
    
    custom_js = """
    <script type="text/javascript">
    function highlightEdgesAndNodes(params) {
        // Dim all nodes and edges
        var allNodes = network.body.data.nodes.get();
        var allEdges = network.body.data.edges.get();
        
        allNodes.forEach(node => {
            // Save the original color if it's not already saved
            if (!node.originalColor) {
                node.originalColor = node.color;
            }
            network.body.data.nodes.update({id: node.id, color: 'rgba(200,200,200,0.2)'});
        });
        
        allEdges.forEach(edge => {
            network.body.data.edges.update({id: edge.id, color: 'rgba(200,200,200,0.2)'});
        });

        // If any node is clicked
        if (params.nodes.length > 0) {
            var selectedNode = params.nodes[0];
            var connectedNodes = network.getConnectedNodes(selectedNode);
            var connectedEdges = network.getConnectedEdges(selectedNode);

            // Highlight the selected node with its original color
            network.body.data.nodes.update({id: selectedNode, color: network.body.data.nodes.get(selectedNode).originalColor});

            // Highlight the connected nodes with their original colors
            connectedNodes.forEach(node => {
                var originalColor = network.body.data.nodes.get(node).originalColor;
                network.body.data.nodes.update({id: node, color: originalColor});
            });
            
            // Highlight the connected edges with yellow color
            connectedEdges.forEach(edge => {
                network.body.data.edges.update({id: edge, color: 'yellow'});
            });
        }
    }
    network.on("click", highlightEdgesAndNodes);
    </script>
    """

    html_content = html_content.replace("</body>", custom_js + "</body>")
    return html_content

# Create and display the knowledge graph
html_content = create_knowledge_graph(data)

# Display the graph in Streamlit
components.html(html_content, height=750)