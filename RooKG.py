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

# Split genres into separate rows
descriptors_data = descriptors_data.assign(Genre=descriptors_data['Genre'].str.split(',')).explode('Genre').reset_index(drop=True)

# Define a color mapping for each column header
color_map = {
    'Artist': '#e07c3e',           # Orange
    'Genre': '#1f77b4',            # Blue
    'Set Day': '#2ca02c',          # Green
    'Roo Location': '#9467bd',     # Purple
    'Stage Name': '#8c564b',       # Brown
}

# Create a Network graph object
net = Network(notebook=True, width="1200px", height="720px", cdn_resources='remote', font_color='white', bgcolor="#222222", select_menu=True, filter_menu=True)

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

    # Add nodes and edges to the network
    for entry in data:
        artist = str(entry[columns.get_loc('Artist')])  # Ensure ID is a string
        net.add_node(artist, label=artist, title=artist, color=color_map['Artist'], size=artist_size, shape=shape_map['Artist'], font={'size': 20, 'vadjust': 25})

        genres = entry[columns.get_loc('Genre')].split(', ')
        for genre in genres:
            frequency = genre_frequency[genre]
            node_size = min_size + scaling_factor * (frequency / max_frequency)  # Ensure minimum size
            genre = str(genre)  # Ensure ID is a string
            net.add_node(genre, label=genre, title=genre, color=color_map['Genre'], size=node_size, shape=shape_map['Genre'])
            net.add_edge(genre, artist)

        set_days = [str(entry[columns.get_loc('Set Day')]), str(entry[columns.get_loc('2nd Set Day')]), str(entry[columns.get_loc('3rd Set Day')])]  # Ensure IDs are strings
        roo_locations = [str(entry[columns.get_loc('Roo Location')]), str(entry[columns.get_loc('2nd Set Roo Location')]), str(entry[columns.get_loc('3rd Set Roo Location')])]  # Ensure IDs are strings
        stage_names = [str(entry[columns.get_loc('Stage Name')]), str(entry[columns.get_loc('2nd Set Stage Name')]), str(entry[columns.get_loc('3rd Set Stage Name')])]  # Ensure IDs are strings

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
                for genre in genres:
                    net.add_edge(stage_name, genre)  # Add new relationship: Genre to Stage Name

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
          "iterations": 1000,
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

    # Generate the HTML content as a string
    html_content = net.generate_html()

    # Write the HTML content to a file with utf-8 encoding
    with open('knowledge_graph.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

create_knowledge_graph(descriptors_data.values.tolist(), descriptors_data.columns)

# Display the graph in the Streamlit app
html_path = 'knowledge_graph.html'
try:
    with open(html_path, 'r', encoding='utf-8') as HtmlFile:
        html_content = HtmlFile.read()

    components.html(html_content, height=1000, width=1000)

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
- **Explore genres, stages, and days**: Now you can also see which genres are performing on specific stages and days by selecting a genre, stage name, or set day from the dropdown menu.
- **Filter edges for deeper insight**: Use the edge filter options ("to" and "from") to understand the relationships better. For example, you can see which artists are performing at a specific stage or on a particular day, and which genres are associated with a stage or day.
- **Reset Selection** by clicking "Reset Selection" to clear the current filter and return the graph to its default view, showing all nodes and edges.
- **Pls ignore** the 'edge'>>'id'>> filtering function, it's showing the unique identifiers instead of labels, idk how to fix it >.< !!

## Hope you enjoy this! - Liezl teehee <3 
Wanna fork this code and make your own? Here's my [GitHub](https://github.com/liezzzlll). 

[My personal site](https://liezzzlll.github.io/liezzzlll/) 
""")