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

# Normalize and explode the genres into separate rows, ensuring to strip spaces and handle case insensitivity
descriptors_data['Genre'] = descriptors_data['Genre'].str.lower().str.split(',')
descriptors_data = descriptors_data.explode('Genre').reset_index(drop=True)
descriptors_data['Genre'] = descriptors_data['Genre'].str.strip()

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

'UNK' means I didn't see any info about this artist, so lmk if you have any deets regarding any unknowns by [responding to the reddit thread](https://www.reddit.com/r/bonnaroo/comments/1cyu135/bonnaroo_2024_knowledge_graph/)!

## Play Around With the Nodes!

- **Nodes**: Represent the entities in the graph, such as "Artist," "Genre," "Set Day," "Roo Location," and "Stage Name." Each node can have various properties like size, color, label, etc.
- **Edges**: Represent the relationships or connections between the nodes, such as an artist being associated with a particular genre or the day they are playing, etc!
- Move the map around by dragging it, using the arrows at the corner of the graph, or your keyboard!
            
Wheeee!!! 
            
For more information on using the filter feature, see [explanation below](#how-to-explore-the-bonnaroo-music-festival-graph).

For the daily schedule, [see below](#bonnaroo-daily-schedule)! Remember, you can search for an artist, genre, set day, Roo location, and stage name in the knowledge graph above! For Thursday to Sunday, I've linked my friend's Spotify playlists that she curated per day!

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
        genres = entry[columns.get_loc('Genre')].split(',')
        genre_frequency.update(genre.strip().lower() for genre in genres)

    
    # Scale the size of nodes based on the number of artists in each genre
    max_frequency = max(genre_frequency.values(), default=1)  # default=1 to handle empty data
    scaling_factor = 30
    min_size = 30
    artist_size = 15

    # Use sets to track added nodes
    added_nodes = set()
    
    # Add nodes and edges to the network
    for entry in data:
        artist = str(entry[columns.get_loc('Artist')]).strip()
        if artist not in added_nodes:
            net.add_node(artist, label=artist, title=artist, color=color_map['Artist'], size=artist_size, shape=shape_map['Artist'], font={'size': 20, 'vadjust': 25})
            added_nodes.add(artist)
        
        genres = [genre.strip().lower() for genre in entry[columns.get_loc('Genre')].split(',')]
        for genre in genres:
            node_size = min_size + scaling_factor * (genre_frequency[genre] / max_frequency)
            if genre not in added_nodes:
                net.add_node(genre, label=genre, title=genre, color=color_map['Genre'], size=node_size, shape=shape_map['Genre'])
                added_nodes.add(genre)
            net.add_edge(artist, genre)

        # Loop to manage additional properties dynamically
        property_types = [('Set Day', 'Set Day'), ('Roo Location', 'Roo Location'), ('Stage Name', 'Stage Name')]
        for prop, col_key in property_types:
            for suffix in ['', '2nd ', '3rd ']:
                prop_name = f'{suffix}{prop}'
                if prop_name in columns:
                    item = str(entry[columns.get_loc(prop_name)]).strip()
                    if item and item != 'nan':
                        if item not in added_nodes:
                            net.add_node(item, label=item, title=item, color=color_map[col_key], shape=shape_map[col_key], font={'size': 20, 'vadjust': 25})
                            added_nodes.add(item)
                        net.add_edge(artist, item)
                        for genre in genres:
                            net.add_edge(genre, item)  # Adding edges from genre to set day, location, and stage

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

""")

# Bonnaroo Daily Schedule
st.title("Bonnaroo Daily Schedule")

# Tuesday
st.header("Tuesday")
st.image("img/2024_outeroo_tue.png", caption="Outeroo Tuesday")

# Wednesday
st.header("Wednesday")
st.image("img/2024_outeroo_wed.png", caption="Outeroo Wednesday")

# Thursday
st.header("Thursday")
st.image("img/2024_centeroo_thu.png", caption="Centeroo Thursday")
st.image("img/2024_outeroo_thu.png", caption="Outeroo Thursday")
st.markdown("[Thursday Sets Spotify Playlist](https://open.spotify.com/playlist/6Z7TF98QOf4zHifNgWEGCe?si=X7O5gkvhRKmcAiBYSAXeLw&pi=u-KX-YB9ChSWyC)")

# Friday
st.header("Friday")
st.image("img/2024_centeroo_fri.png", caption="Centeroo Friday")
st.image("img/2024_outeroo_fri.png", caption="Outeroo Friday")
st.markdown("[Friday Sets Spotify Playlist](https://open.spotify.com/playlist/1O1dR7G7l7mRY1tGqR5UbW?si=ZQ1WK2smSMKXGIMpOwqp8g&pi=u-5FiNTvwUTCy9)")

# Saturday
st.header("Saturday")
st.image("img/2024_centeroo_sat.png", caption="Centeroo Saturday")
st.image("img/2024_outeroo_sat.png", caption="Outeroo Saturday")
st.markdown("[Saturday Sets Spotify Playlist](https://open.spotify.com/playlist/01HarVumXcUXWKylX6e45C?si=tx7HmPLWRC-vbEJsB9gRhg&pi=u-hIQ9CyPETgWs)")


# Sunday
st.header("Sunday")
st.image("img/2024_centeroo_sun.png", caption="Centeroo Sunday")
st.image("img/2024_outeroo_sun.png", caption="Outeroo Sunday")
st.markdown("[Sunday Sets Spotify Playlist](https://open.spotify.com/playlist/1XsJCp8uR8c2x1LXmDKa0y?si=ECk2AElDSfeWHMIykz-jkA&pi=u-spArrRfwR5u1)")

st.markdown("""
## Hope you enjoy this! - Liezl teehee <3 
Wanna fork this code and make your own? Here's my [GitHub](https://github.com/liezzzlll). 

[My personal site](https://liezzzlll.github.io/liezzzlll/) 

""")