import networkx as nx
from . import utils
from copy import deepcopy
import numpy as np
import pyphi

def create_ces_graph(distinctions, relations=None, invert_3face_edge=True):
    '''
    Create CES dict.

    Note: 2-relations only.

    Parameters
    ----------
    distinctions
    relations

    Returns
    -------
    CES : dict[face-degree] --> networkx graph, i.e. {4 : nx.Graph, 5 : nx.MultiDigraph)
    '''

    def _add_distinctions(G, distinctions):
        for d in distinctions:
            attr = dict(phi=d.phi, node_indices=d.mechanism,
                        node_label=utils.node_ixs2label(d.mechanism, d.node_labels))
            G.add_node(utils.node_ixs2label(d.mechanism, d.node_labels), **attr)
        return G

    def _add_4face_edge():
        CES[4].add_edge(mech_label1, mech_label2, color='blue', purview=face.purview)

    def _add_3face_edge(invert_3face_edge):
        triangle_type = eval_rel_3face_type(face)
        edge_color = 'green' if triangle_type == 'effect' else 'red'

        base_mech = eval_rel_3face_base(face)

        if not invert_3face_edge: # original
            if base_mech == mech1:
                arrow_base_label = mech_label1
                arrow_point_label = mech_label2
            elif base_mech == mech2:
                arrow_base_label = mech_label2
                arrow_point_label = mech_label1
            else:
                raise ValueError(f'Inconsistent mechanisms ({mech1}, {mech2}) and {base_mech}')
        else: # new proposed convention
            if base_mech == mech1:
                arrow_base_label = mech_label2
                arrow_point_label = mech_label1
            elif base_mech == mech2:
                arrow_base_label = mech_label1
                arrow_point_label = mech_label2
            else:
                raise ValueError(f'Inconsistent mechanisms ({mech1}, {mech2}) and {base_mech}')

        CES[3].add_edge(arrow_base_label, arrow_point_label, color=edge_color, purview=face.purview)

    def _add_2face_edge():
        face_type = eval_rel_2face_type(face)
        if face_type=='effect_effect':
            CES[2].add_edge(mech_label1, mech_label2, color='green', purview=face.purview)
            # CES[2].add_edge(mech_label2, mech_label1, color='green', purview=face.purview)

        elif face_type=='cause_cause':
            CES[2].add_edge(mech_label1, mech_label2, color='red', purview=face.purview)
            # CES[2].add_edge(mech_label2, mech_label1, color='red', purview=face.purview)

        elif face_type=='cause_effect':
            CES[2].add_edge(mech_label1, mech_label2, color='orange', purview=face.purview)
        else: # effect_cause
            CES[2].add_edge(mech_label2, mech_label1, color='orange', purview=face.purview)

    relations = filter_relations_by_degree(relations, 2)  # filter 2-relations

    CES = {}
    # 4-face graph
    G = nx.Graph()
    CES[4] = _add_distinctions(G, distinctions)

    # 3-face multi digraph
    G = nx.MultiDiGraph()
    CES[3] = _add_distinctions(G, distinctions)

    # 2-face multi digraph
    G = nx.MultiDiGraph()
    CES[2] = _add_distinctions(G, distinctions)

    # ADD RELATIONS
    for rel in relations:
        distinction1, distinction2 = list(rel)
        mech1, mech2 = distinction1.mechanism, distinction2.mechanism
        mech_label1, mech_label2 = utils.nodes_ixs2label([mech1, mech2], distinction1.node_labels)

        sorted_faces = sorted(list(rel.faces), key=len, reverse=True)

        for face in sorted_faces:
            face_degree = len(face)
            if face_degree == 4:
                _add_4face_edge()
            elif face_degree == 3:
                _add_3face_edge(invert_3face_edge=invert_3face_edge)
            elif face_degree==2:
                _add_2face_edge()
            else:
                pass
    return CES

def eval_rel_2face_type(face):
    '''
    Returns whether relation 2-face is c-c, e-e, c-e or e-c.
    '''

    assert len(face) == 2, 'Face is not of 2nd degree.'

    purview1, purview2 = list(face)
    direction1, direction2 = str(purview1.direction), str(purview2.direction)

    if direction1=='CAUSE' and direction2=='CAUSE':
        return 'cause_cause'
    elif direction1=='CAUSE' and direction2=='EFFECT':
        return 'cause_effect'
    elif direction1=='EFFECT' and direction2=='CAUSE':
        return 'effect_cause'
    elif direction1 == 'EFFECT' and direction2 == 'EFFECT':
        return 'effect_effect'
    else:
        raise ValueError(f'Weird purview directions: {direction1} and {direction2}')

def eval_rel_3face_type(face):
    '''
    Returns whether relation 3-face is dominated by cause or effect purviews.

    Parameters
    ----------
    face :

    Returns
    -------
    'cause' : face is composed of two cause purviews and one effect purview
    'effect': face is composed of two effect purviews and one cause purview
    '''
    assert len(face) == 3, 'Face is not of 3rd degree.'

    purviews = list(face)
    directions = [str(p.direction) for p in purviews]
    n_cause = directions.count('CAUSE')
    if n_cause == 2:  # two causes and one effect
        return 'cause'
    else:
        return 'effect'


def eval_rel_3face_base(face):
    '''
    Returns mechanism of distinction with two purviews in a 3-face relation.

    Returns
    -------
    base_mech : tuple with mechanism indices (e.g. (1, 2, 3))
    '''
    assert len(face) == 3, 'Face is not of 3rd degree.'

    mechs = [f.mechanism for f in list(face)]
    unique_mechs = list(set(mechs))

    if mechs.count(unique_mechs[0]) == 2:
        base_mech = unique_mechs[0]
    else:
        base_mech = unique_mechs[1]
    return base_mech

def get_max_face(relation):
    '''Returns face with largest degree.'''
    i = np.argmax([len(f) for f in relation.faces])
    return list(relation.faces)[i]

def filter_contiguous_distinctions(distinctions):
    return [d for d in distinctions if utils.is_contiguous(d.mechanism)]

def filter_relations_by_degree(relations, degree):
    '''
    Filter relations by relation degree.

    Parameters
    ----------
    relations : list of relations
    degree : int, degree of relation (e.g. 2-relation, i.e. relation between 2 distinctions)

    Returns
    -------
    list of relations of given degree
    '''
    return [r for r in relations if len(r) == degree]

def filter_faces_by_degree(faces, degree):
    '''
    Filter faces by degree
    '''
    return [f for f in list(faces) if len(f) == 4]

def filter_relations_by_distinctions(relations, distinctions):
    '''
    Filter relations within a set of distinctions.

    Parameters
    ----------
    relations
    distinctions

    Returns
    -------
    filtered relations
    '''
    mechs = [d.mechanism for d in distinctions]
    filtered_rels = []
    for rel in relations:
        rel_distinctions = list(rel)
        rel_mechs = [d.mechanism for d in rel_distinctions]

        all_rel_mechs_in_mechs = np.all([m in mechs for m in rel_mechs])
        if all_rel_mechs_in_mechs:
            filtered_rels.append(rel)
    return filtered_rels

def filter_ces_graph_to_context(G, seed):
    return G.subgraph([seed])

def filter_ces_to_context(CES, distinction_labels, external=True):
    '''
    Filter CES to the context of a list of distinctions (given by its mechanism labels)
    '''
    condition = any if external else all
    new_CES = deepcopy(CES)

    edges_to_remove = []
    for n, G in new_CES.items():
        for e in G.edges:
            mechs = e[:2] if is_multi_graph(G) else e

            if not condition(m in distinction_labels for m in mechs):
                edges_to_remove.append(e)
        new_CES[n].remove_edges_from(edges_to_remove)
    return new_CES

def is_multi_graph(G):
    if type(G) in [type(nx.MultiGraph()), type(nx.MultiDiGraph())]:
        return True
    else:
        return False

def filter_ces_by_higher_face_purview_overlap(CES):
    new_CES = deepcopy(CES)
    new_CES[3] = filter_G_by_coG_purview_overlap(CES[3], CES[4])
    new_CES[2] = filter_G_by_coG_purview_overlap(CES[2], CES[4])
    new_CES[2] = filter_G_by_coG_purview_overlap(CES[2], CES[3])

    return new_CES

def filter_G_by_coG_purview_overlap(G, coG):
    '''
    Filter k-faces graph by k'-faces graph: k-face (edge) is removed if the
    overlap purview if it is a subset of the overlap purview of a k'-face
    in that 2-relation.

    Parameters
    ----------
    G : constrained ces-graph
    coG : constraining ces-graph
    '''

    is_G_multi = is_multi_graph(G)
    is_coG_multi = is_multi_graph(coG)
    edges_to_remove = []
    if (is_G_multi and not is_coG_multi):
        # print('CASE: constrained by 4')
        for e in G.edges:
            G_purview = G.edges[e]['purview']
            co_e = e[:2]
            if coG.has_edge(*co_e):
                coG_purview = coG.edges[co_e]['purview']
                # if len(G_purview) <= len(coG_purview):
                if G_purview.issubset(coG_purview):
                    edges_to_remove.append(e)

    elif is_G_multi and is_coG_multi:  # e.g. CES[2] constrained by CES[3]
        # print('CASE: constrained by 3')
        for e in G.edges:
            G_purview = G.edges[e]['purview']

            # Get constraining edges (co_edges)
            base_e1 = e[:2]  # e.g. ('ABC', 'BC', 1) --> ('ABC', 'BC')
            base_e2 = (base_e1[1], base_e1[0])  # inverted edge e.g. ('BC', 'ABC')
            co_edges = []
            for base_e in [base_e1, base_e2]:
                i = 0
                flag = True
                while flag:
                    co_e = base_e + (i,)
                    if coG.has_edge(*co_e):
                        co_edges.append(co_e)
                        i += 1
                    else:
                        flag = False
            # Test constrained edge (e) against constraining edges (co_edges
            for co_e in co_edges:
                coG_purview = coG.edges[co_e]['purview']
                # print(f"e:{e} -> p:{str(G_purview).upper()} | co_e:{co_e} -> co_p:{str(coG_purview).upper()}")

                if G_purview.issubset(coG_purview):
                    edges_to_remove.append(e)
                    # print('>> Edge removed.')
                    break  # edge is subset in coG --> EDGE REMOVED
    else:
        raise ValueError('Case not implemented.')

    new_G = G.copy()
    new_G.remove_edges_from(edges_to_remove)
    return new_G

def sort_distinctions(distinctions, n_nodes):
    '''Sort distinctions by mechanism'''
    all_mechs = list(pyphi.utils.powerset(range(n_nodes), nonempty=True))

    mechs = [d.mechanism for d in distinctions]

    sorted_distinctions = []
    for m in all_mechs:
        if m in mechs:
            ix = mechs.index(m)
            sorted_distinctions.append(distinctions[ix])
    return sorted_distinctions

def decompose_graph_by_edge_attribute(G, attribute):
    edge_attributes = nx.get_edge_attributes(G, attribute)

    unique_vals = list(set(edge_attributes.values()))

    decomposed_G = {}
    for val in unique_vals:
        dG = G.copy()
        edges_to_remove = [edge for edge, x in edge_attributes.items() if x != val]
        dG.remove_edges_from(edges_to_remove)
        decomposed_G[val] = dG
    return decomposed_G


def decompose_ces_by_edge_attribute(CES, attribute):
    dCES = {}
    for n, G in CES.items():
        dG = decompose_graph_by_edge_attribute(G, attribute)
        dCES[n] = dG
    return dCES

def _fix_decomposed_facecolor_ces_graph(dCES):
    '''
    Add missing graphs and fix order for plotting.
    '''
    # 4-face
    if 'blue' not in dCES[4].keys():
        dCES[4]['blue'] = nx.Graph()
    # 3-face
    for c in ['green', 'red']:
        if c not in dCES[3].keys():
            dCES[3][c] = nx.MultiDiGraph()
    # 2-face
    if 'orange' not in dCES[2].keys():
        dCES[2]['orange'] = nx.MultiDiGraph()

    for c in ['green', 'red']:
        if c in dCES[2].keys():
            dCES[2][c] = dCES[2][c].to_undirected()
        else:
            dCES[2][c] = nx.MultiGraph()
    dCES[2] = {k:dCES[2][k] for k in ['green', 'red', 'orange']}
    return dCES

def decompose_ces_by_facecolor(CES, facecolor_attribute='color'):
    dCES = decompose_ces_by_edge_attribute(CES, facecolor_attribute)
    dCES = _fix_decomposed_facecolor_ces_graph(dCES)
    return dCES

