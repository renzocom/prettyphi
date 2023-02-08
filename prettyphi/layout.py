import numpy as np
import itertools
from . import utils


################
# GRAPH LAYOUT #
################

def offset_pos(pos, x=0, y=0):
    '''
    Parameters
    ----------
    pos : dict[node] = (x, y)
    x, y : float, offset

    Returns
    -------
    pos with offset
    '''
    new_pos = {}
    for key in pos.keys():
        new_pos[key] = np.array([pos[key][0] + x, pos[key][1] + y])
    return new_pos

def warp_hasse_layout(node2pos, rho=0.1, mode='exponential'):
    '''
    Warps hasse layout.

    Parameters
    ----------
    node2pos : {node : pos}
    rho : 0 < float

    Returns
    -------
    node2pos
    '''

    def exponential_warp(pos):
        '''
        y = rho * x^2
        '''
        x, y = pos
        xx = x - (end - ini) / 2
        yy = y + rho * xx ** 2
        return x, yy

    def circle_warp(pos):
        '''
        circle: y = - np.sqrt(r^2 - (x - a)^2) + b
        '''
        x, y = pos
        center_x, center_y = center
        radius = center_y / rho
        y_offset = - np.sqrt(radius ** 2 - (x - center_x) ** 2) + center_y
        yy = y + y_offset
        return x, yy

    if rho == 0:
        return node2pos

    pos = np.array([list(pos) for pos in node2pos.values()])
    X, Y = pos[:, 0], pos[:, 1]
    ini, end = min(X), max(X)
    center = ((end - ini) / 2, max(Y))

    if mode == 'exponential':
        return {node: exponential_warp(pos) for node, pos in node2pos.items()}

    elif mode == 'circle':
        return {node: circle_warp(pos) for node, pos in node2pos.items()}
    else:
        raise ValueError("mode must be 'exponential' or 'circle'")


def hasse_layout(n_elements, warp=0, triangle_base=1, warp_mode='exponential'):
    '''
    Generates the Hasse diagram layout out of the contiguous sets in the powerset of 'n_elements'.

    Parameters
    ----------
    n_elements : int
    warp : 0 < float
    triangle_base : float

    Returns
    -------
    dict : {sets : (x,y)}

    '''

    all_sets = [list(itertools.combinations(range(n_elements), n)) for n in range(1, n_elements + 1)]  # list of lists

    contiguous_sets = [[x for x in sets if utils.is_contiguous(x)] for sets in all_sets]

    contiguous_sets_flat = np.sum(contiguous_sets, dtype='object')

    y_scale = triangle_base
    ys = [len(x) * y_scale for x in contiguous_sets_flat]

    xs = []
    x_ini = 0
    for order, sets in enumerate(contiguous_sets):
        xs_tmp = [x_ini + n * triangle_base for n in range(len(sets))]
        xs += xs_tmp
        x_ini += triangle_base / 2

    # xs = list(np.array(xs) / 100)
    # ys = list(np.array(ys) / 100)

    pos = list(zip(xs, ys))

    node2pos = {sets: np.array(xy) for sets, xy in zip(contiguous_sets_flat, pos)}
    if warp != 0:
        node2pos = warp_hasse_layout(node2pos, warp, mode=warp_mode)
    return node2pos