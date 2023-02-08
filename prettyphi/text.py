import numpy as np
from . import utils

def distinction_str(distinction, pad=True, common_pad=True, forget=False, horizontal=True):
    '''
    Returns str with mechanism representation.

    Parameters
    ----------
    mech : pyphi.models.mechanism.Concept
    horizontal : bool
        Whether mechanism is formatted in vertical or horizontal orientation
    remove_pad : bool
    forget : bool
        Changes letters for x's
    '''
    labels = distinction.node_labels

    mech, cause, effect = utils.node_ixs2label(distinction.mechanism, labels), utils.node_ixs2label(distinction.cause_purview, labels), utils.node_ixs2label(distinction.effect_purview, labels)

    if pad:
        mech, cause, effect = pad_mech_label(mech, labels), pad_mech_label(cause, labels), pad_mech_label(effect, labels)
    if forget:
        mech, cause, effect = forget_str([mech, cause, effect])

    if horizontal:
        if not common_pad:
            mech, cause, effect = remove_common_pad([mech, cause, effect])
        return f"[{cause}] -> ({mech}) -> [{effect}]"
    else:
        mech, cause, effect = remove_common_pad([mech, cause, effect])
        n = np.max([len(mech), len(cause), len(effect)])
        dash = '-' * n
        return f"{mech}\n{dash}\n{effect}\n{cause}"

def pad_mech_label(label, node_labels):
    """
    Pad mechanism label str.

    Parameters
    ----------
    node_ixs : str
    node_labels : pyphi.labels.NodeLabels

    Returns
    -------
    str

    Example
    -------
    >>> pad_mech_label('CD', ['A', 'B', 'C', 'D'])
    '  CD'

    >>> pad_mech_label('BD', ['A', 'B', 'C', 'D'])
    ' C D'

    """
    s = " " * len(node_labels)
    for c in label:
        ix = node_labels.index(c)
        s = s[:ix] + c + s[ix + 1:]
    return s