from . import layout, utils
import matplotlib.pyplot as plt
import networkx as nx

def plot_circular_ces_graph(CES, figsize=(15, 5)):
    pos = nx.layout.circular_layout(CES[3], scale=1)
    pos_labels = nx.layout.circular_layout(CES[3], scale=1.3)
    # pos_labels = offset_pos(pos, x=0, y=0.15)
    _plot_ces_graph(CES, pos, pos_labels, figsize=figsize)

def plot_hasse_ces_graph(CES, n_nodes, node_labels, figsize=(15, 5)):
    pos = layout.hasse_layout(n_nodes)
    pos = {utils.node_ixs2label(mech, node_labels): xy for mech, xy in pos.items()}
    pos_labels = layout.offset_pos(pos, x=0, y=0.35)

    _plot_ces_graph(CES, pos, pos_labels, figsize=figsize)

def plot_graph(G, pos, pos_labels, ax=None, edgecolor_field='color'):
    '''
    '''
    if ax is None:
        fig, ax = plt.subplots()

    ax.set_aspect('equal', adjustable='box')
    nx.draw_networkx_nodes(G, pos=pos, ax=ax, edgecolors='k', margins=0.2)

    if edgecolor_field is not None:
        edge_colors = nx.get_edge_attributes(G, edgecolor_field)
        nx.draw_networkx_edges(G, pos=pos, ax=ax, edge_color=edge_colors.values())
    else:
        nx.draw_networkx_edges(G, pos=pos, ax=ax, edge_color='k')
    nx.draw_networkx_labels(G, pos_labels, ax=ax);
    # edge_labels = nx.get_edge_attributes(G, 'purview')
    # nx.draw_networkx_edge_labels(CES[3], pos, edge_labels=edge_labels)

def _plot_ces_graph(CES, pos, pos_labels, figsize=(15, 5)):
    fig, axes = plt.subplots(ncols=3, figsize=figsize)
    # 4-FACES
    ax = axes[0]
    plot_graph(CES[4], pos, pos_labels, ax=ax, edgecolor_field='color')
    ax.set_title('4-Faces')

    # 3-FACES
    ax = axes[1]
    plot_graph(CES[3], pos, pos_labels, ax=ax, edgecolor_field='color')
    ax.set_title('3-Faces')

    # 2-FACES
    ax = axes[2]
    plot_graph(CES[2], pos, pos_labels, ax=ax, edgecolor_field='color')
    ax.set_title('2-Faces')