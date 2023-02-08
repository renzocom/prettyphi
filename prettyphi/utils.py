import numpy as np

def is_contiguous(x):
    '''
    Checks if indices in array are contiguous (e.g. [3,4,5,6] but not [3,5,6])
    Parameters
    ----------
    x : 1d array of indices

    Returns
    -------
    bool
    '''
    d_x = np.diff(x)
    if np.all(d_x == 1):
        return True
    else:
        return False

def node_ixs2label(ixs, node_labels):
    '''
    Convert node indices to labels.

    Parameters
    ----------
    ixs : tuple of ints
    node_labels : list of str

    Returns
    -------
    str

    Examples
    --------
    >>> node_ixs2label((3,4,5), ['H', 'G', 'F', 'E', 'D', 'C', 'B', 'A'])
    'EDC'
    '''
    return ''.join(node_labels[ix] for ix in ixs)

def node_label2ixs(label, node_labels):
    '''
    Convert node labels to indices.

    Parameters
    ----------
    label : str
    node_labels : list of str

    >>> node_label2ixs('EDC', ['H', 'G', 'F', 'E', 'D', 'C', 'B', 'A'])
    (3, 4, 5)
    '''
    return tuple([node_labels.index(s) for s in label])

def nodes_ixs2label(nodes_ixs, node_labels):
    '''
    Converts list of node indices to labels.

    Parameters
    ----------
    nodes_ixs : list of indices list
    node_labels : list of str

    Returns
    -------
    list of str

    '''
    return [node_ixs2label(ixs, node_labels) for ixs in nodes_ixs]