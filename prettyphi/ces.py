import networkx as nx
from . import utils
from copy import deepcopy
import numpy as np
import pyphi

def create_ces_graph(distinctions, relations=None):
    '''
    Parameters
    ----------
    distinctions
    relations

    Returns
    -------
    CES : dict[face-degree] --> networkx graph, i.e. {4 : nx.Graph, 5 : nx.MultiDigraph)
    '''

    def add_distinctions(G, distinctions):
        for d in distinctions:
            attr = dict(phi=d.phi, node_indices=d.mechanism,
                        node_label=utils.node_ixs2label(d.mechanism, d.node_labels))
            G.add_node(utils.node_ixs2label(d.mechanism, d.node_labels), **attr)
        return G

    CES = {}
    # 4-face graph
    G = nx.Graph()
    CES[4] = add_distinctions(G, distinctions)

    # 3-face multi digraph
    G = nx.MultiDiGraph()
    CES[3] = add_distinctions(G, distinctions)

    # 2-face multi digraph
    # TODO

    ## 4-face graph
    relations = filter_relations_by_degree(relations, 2)  # filter 2-relations

    # ADD RELATIONS
    for rel in relations:
        distinction1, distinction2 = list(rel)
        mech1, mech2 = distinction1.mechanism, distinction2.mechanism
        label1, label2 = utils.nodes_ixs2label([mech1, mech2], distinction1.node_labels)

        sorted_faces = sorted(list(rel.faces), key=len, reverse=True)

        for face in sorted_faces:
            face_degree = len(face)
            if face_degree == 4:
                CES[4].add_edge(label1, label2, color='blue', purview=face.purview)
            elif face_degree == 3:
                # test superset condition!

                add_face3 = False
                face4_not_present = (label1, label2) not in CES[4].edges  # 4-face exists already

                if face4_not_present:
                    add_face3 = True
                else:
                    face4_purview = CES[4].edges[label1, label2]['purview']
                    face3_purview = face.purview
                    is_superset_of_face4 = len(face3_purview) > len(face4_purview)  # 3-face is superset of 4-face
                    if is_superset_of_face4:
                        add_face3 = True

                if add_face3:
                    triangle_type = eval_rel_3face_type(face)
                    edge_color = 'green' if triangle_type == 'effect' else 'red'

                    base_mech = eval_rel_3face_base(face)
                    if base_mech == mech1:
                        arrow_base_label = label1
                        arrow_point_label = label2
                    elif base_mech == mech2:
                        arrow_base_label = label2
                        arrow_point_label = label1
                    else:
                        raise ValueError(f'Inconsistent mechanisms ({mech1}, {mech2}) and {base_mech}')

                    CES[3].add_edge(arrow_base_label, arrow_point_label, color=edge_color, purview=face.purview)

            else:
                # TODO add lower degree faces
                pass
    return CES

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

    Parameters
    ----------
    face

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