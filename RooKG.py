import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import networkx as nx
from collections import Counter
from pyvis.network import Network
from IPython.core.display import display, HTML

# Read the new CSV file
descriptors_data = pd.read_csv("Bonnaroo_KG.csv")

# Convert DataFrame to a list of lists with all entries as strings
project_data = descriptors_data.astype(str).values.tolist()

# Define a color mapping for each column header
color_map = {
    'Artist': '#e07c3e',           # Orange
    'Genre': '#1f77b4',            # Blue
    'Set Day': '#2ca02c',          # Green
    'Roo Location': '#9467bd',     # Purple
    'Stage Name': '#8c564b',       # Brown
}

# Create a Network graph object
net = Network(notebook=True, width="1200px", height="720px", cdn_resources='remote', font_color='white', bgcolor="black", select_menu=True, filter_menu=False)

# Adjust jiggle physics
net.set_options("""
var options = {
  "physics": {
    "barnesHut": {
      "gravitationalConstant": -50000,
      "centralGravity": 0.2,
      "springLength": 250,
      "springConstant": 0.05,
      "damping": 0.1
    },
    "minVelocity": 0.5
  }
}
""")

st.title('Bonnaroo 2024 Music Festival Knowledge Graph')

# Add description before presenting the knowledge graph
st.markdown("""
Hi Bonnarooians!  I used the data from the [genre venn diagram](https://www.reddit.com/r/bonnaroo/comments/1cllv19/2024_roo_genre_venn_diagram_is_here/?share_id=bMZmCCc3Oa8fHzdBxTHYd&utm_content=1&utm_medium=ios_app&utm_name=ioscss&utm_source=share&utm_term=1) that someone had made to make this interactive knowledge graph, combined with info about the day(s) the artist is playing and stage location.
            
Note that I didn't add all of the Outeroo activities (i.e. yoga, tarot reading, etc. that didn't quite fit a "genre")
            
## Play Around With the Nodes!

- **Nodes**: Represent the entities in the graph, such as "Artist," "Genre," "Set Day," "Roo Location," and "Stage Name." Each node can have various properties like size, color, label, etc.
- **Edges**: Represent the relationships or connections between the nodes, such as an artist being associated with a particular genre or the day they are playing, etc!
- Move the map around by dragging it!
            
Wheeee!!! 
            
For more information on using the filter feature, see [explanation below](#how-to-explore-the-bonnaroo-music-festival-graph).
""")

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

def create_knowledge_graph(data, columns):
    # Initialize the network
    net = Network(notebook=True)
    
    # Calculate the frequency of each genre
    genre_frequency = Counter()
    for entry in data:
        genres = entry[columns.get_loc('Genre')].split(', ')
        genre_frequency.update(genres)

    # Scale the size of nodes based on the number of artists in each genre
    max_frequency = max(genre_frequency.values())
    scaling_factor = 30  # Adjust the scaling factor as needed
    min_size = 30        # Minimum size for genre nodes
    artist_size = 15     # Fixed size for artist nodes

    # Debug: write max frequency
    st.write("Max Frequency:", max_frequency)

    # Add nodes and edges to the network
    for entry in data:
        artist = entry[columns.get_loc('Artist')]
        net.add_node(artist, label=artist, title=artist, color=color_map['Artist'], size=artist_size, shape=shape_map['Artist'], font={'size': 20, 'vadjust': 25})

        genres = entry[columns.get_loc('Genre')].split(', ')
        for genre in genres:
            frequency = genre_frequency[genre]
            node_size = min_size + scaling_factor * (frequency / max_frequency)  # Ensure minimum size
            # Debug: write node size for each genre
            st.write(f"Genre: {genre}, Frequency: {frequency}, Node Size: {node_size}")
            net.add_node(genre, label=genre, title=genre, color=color_map['Genre'], size=node_size, shape=shape_map['Genre'])
            net.add_edge(genre, artist)

        set_days = [entry[columns.get_loc('Set Day')], entry[columns.get_loc('2nd Set Day')], entry[columns.get_loc('3rd Set Day')]]
        roo_locations = [entry[columns.get_loc('Roo Location')], entry[columns.get_loc('2nd Set Roo Location')], entry[columns.get_loc('3rd Set Roo Location')]]
        stage_names = [entry[columns.get_loc('Stage Name')], entry[columns.get_loc('2nd Set Stage Name')], entry[columns.get_loc('3rd Set Stage Name')]]

        for set_day, roo_location, stage_name in zip(set_days, roo_locations, stage_names):
            if set_day and set_day != "nan":
                net.add_node(set_day, label=set_day, title=set_day, color=color_map['Set Day'], shape=shape_map['Set Day'], font={'size': 20, 'vadjust': 25})
                net.add_edge(artist, set_day)
            if roo_location and roo_location != "nan":
                net.add_node(roo_location, label=roo_location, title=roo_location, color=color_map['Roo Location'], shape=shape_map['Roo Location'], font={'size': 20, 'vadjust': 25})
                net.add_edge(artist, roo_location)
            if stage_name and stage_name != "nan":
                net.add_node(stage_name, label=stage_name, title=stage_name, color=color_map['Stage Name'], shape=shape_map['Stage Name'], font={'size': 20, 'vadjust': 25})
                net.add_edge(artist, stage_name)

    # Generate the HTML content as a string
    html_content = net.generate_html()

    # Write the HTML content to a file with utf-8 encoding
    with open('knowledge_graph.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

create_knowledge_graph(project_data, descriptors_data.columns)

# Display the graph in the Streamlit app
html_path = 'knowledge_graph.html'
try:
    with open(html_path, 'r', encoding='utf-8') as HtmlFile:
        html_content = HtmlFile.read()

    components.html(html_content, height=800, width=1000)

except FileNotFoundError:
    st.warning(f"HTML file not found at {html_path}.")
except Exception as e:
    st.error(f"An error occurred while reading the HTML file: {e}")

# Details about filtering and navigating the knowledge graph
st.markdown("""
## How to Explore the Bonnaroo Music Festival Graph

**Find your favorites!**
  - Use the dropdown menu labeled "Select a Node by ID" to pick a specific artist, genre, set day, Roo Location, or Stage Name. This will highlight the node and its connections, making it easy to zoom in on the part of the festival you're most excited about! 

**Dive into details!**
- **Choose an artist by clicking directly on their name**: When you select an artist, this will highlight all of the edges and nodes about this artist!

- **Reset Selection** by clicking "Reset Selection" to clear the current filter and return the graph to its default view, showing all nodes and edges.
            
## Hope you enjoy this! - Liezl teehee <3 
""")