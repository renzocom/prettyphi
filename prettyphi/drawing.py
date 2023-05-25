from . import layout, utils
import matplotlib.pyplot as plt
import networkx as nx



def plot_circular_ces_graph(CES, figsize=(15, 5)):
    pos = nx.layout.circular_layout(CES[3], scale=1)
    pos_labels = nx.layout.circular_layout(CES[3], scale=1.3)
    # pos_labels = offset_pos(pos, x=0, y=0.15)
    plot_ces_graph(CES, pos, pos_labels=pos_labels, figsize=figsize)

def plot_hasse_ces_graph(CES, node_labels, figsize=(15, 5), warp=0):
    pos = layout.hasse_layout(CES[3], node_labels, warp=warp)
    pos_labels = layout.offset_pos(pos, x=0, y=0.35)
    plot_ces_graph(CES, pos, pos_labels=pos_labels, figsize=figsize)

def plot_ces_graph(CES, pos, pos_labels=None, figsize=(15, 5)):
    fig, axes = plt.subplots(ncols=3, figsize=figsize)
    # 4-FACES
    ax = axes[0]
    plot_graph(CES[4], pos, pos_labels=pos_labels, ax=ax, edgecolor_field='color')
    ax.set_title('4-Faces')

    # 3-FACES
    ax = axes[1]
    plot_graph(CES[3], pos, pos_labels=pos_labels, ax=ax, edgecolor_field='color')
    ax.set_title('3-Faces')

    # 2-FACES
    ax = axes[2]
    plot_graph(CES[2], pos, pos_labels=pos_labels, ax=ax, edgecolor_field='color')
    ax.set_title('2-Faces')

def plot_graph(G,
               pos=None,
               pos_labels=None,
               node_colors='tab:blue',
               node_labels=None,
               node_size=300,
               node_label_fontsize=12,
               ax=None,
               edgecolor_field=None,
               edgecolor=None):
    '''
    '''
    if ax is None:
        fig, ax = plt.subplots()

    ax.set_aspect('equal', adjustable='box')

    nx.draw_networkx_nodes(G, pos=pos, ax=ax, node_size=node_size, node_color=node_colors, edgecolors='k', margins=0.2)

    if edgecolor_field is not None:
        edge_colors = nx.get_edge_attributes(G, edgecolor_field)
        nx.draw_networkx_edges(G, pos=pos, ax=ax, edge_color=edge_colors.values())
    elif edgecolor is not None:
        nx.draw_networkx_edges(G, pos=pos, ax=ax, edge_color=edgecolor)
    else:
        nx.draw_networkx_edges(G, pos=pos, ax=ax, edge_color='lightgray')

    if pos_labels is not None:
        nx.draw_networkx_labels(G, pos_labels, labels=node_labels, ax=ax, font_size=node_label_fontsize);
    # edge_labels = nx.get_edge_attributes(G, 'purview')
    # nx.draw_networkx_edge_labels(CES[3], pos, edge_labels=edge_labels)

def plot_decomposed_facecolor_ces_graph(dCES, pos, pos_labels=None, figsize=(25, 25)):
    subtitles = [['Full'],['Effect dominated', 'Cause dominated'], ['Effect-Effect', 'Cause-Cause', 'Cause to Effect']]
    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=figsize)

    for i, (n, dG) in enumerate(dCES.items()):
        for j, (c, G) in enumerate(dG.items()):
            ax = axes[i, j]
            plot_graph(G, pos, pos_labels=pos_labels, ax=ax)
            ax.set_title(f'{subtitles[i][j]} {n}-Face')

    fig.delaxes(axes[0][1])
    fig.delaxes(axes[0][2])
    fig.delaxes(axes[1][2])
    plt.tight_layout()