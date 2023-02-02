#
# Healpix utilities
#

import numpy as np
import healpy as hp

# see the documentation for get_edge() about this variable
_edge_vectors = [
    np.asarray([1, 3]), # NE edge
    np.asarray([1]),    # E corner
    np.asarray([0, 1]), # SE edge
    np.asarray([0]),    # S corner
    np.asarray([0, 2]), # SW edge
    np.asarray([2]),    # W corner
    np.asarray([2, 3]), # NW edge
    np.asarray([3])     # N corner
]

# cache used by get_margin()
_suffixes = {}

def get_edge(dk, pix, edge):
    """Get all the pixels at order kk+dk bordering pixel pix.
    See hipscat/pixel_math/README.md for more info.

    Args:
        dk (int): the change in k that we wish to find the margins for.
        pix (int): the healpix pixel to find margin pixels of.
        edge (int): the edge we want to find for the given pixel. (0-7)
            0: NE edge
            1: E corner
            2: SE edge
            3: S corner
            4: SW edge
            5: W corner
            6: NW edge
            7: N corner
    Returns:
        one-dimensional numpy array of long integers, filled with the healpix pixels 
            at order kk+dk that border the given edge of pix.
    """
    if edge < 0 or edge > 7:
        raise ValueError("edge can only be values between 0 and 7 (see docstring)")
        
    if (edge, dk) in _suffixes.keys():
        a = _suffixes[(edge, dk)]
    else:
        # generate and cache the suffix:

        # generate all combinations of i,j,k,... suffixes for the requested edge
        # See https://stackoverflow.com/a/35608701
        a = np.array(np.meshgrid(*[_edge_vectors[edge]]*dk)).T.reshape(-1, dk)
        # bit-shift each suffix by the required number of bits
        a <<= np.arange(2*(dk-1),-2,-2)
        # sum them up row-wise, generating the suffix
        a = a.sum(axis=1)
        # cache for further reuse
        _suffixes[(edge, dk)] = a

    # append the 'pix' preffix
    a = (pix << 2*dk) + a
    return a

def get_margin(kk, pix, dk):
    """Get all the pixels at order kk+dk bordering pixel pix.
    See hipscat/pixel_math/README.md for more info.

    Args:
        kk (int): the healpix order of pix.
        pix (int): the healpix pixel to find margin pixels of.
        dk (int): the change in k that we wish to find the margins for. 
            Must be greater than kk.
    Returns:
        one-dimensional numpy array of long integers, filled with the healpix pixels 
            at order kk+dk that border pix.
    """
    if dk < 1:
        raise ValueError("dk must be greater than kk")
    
    nside = hp.order2nside(kk)

    # get all neighboring pixels
    n = hp.get_all_neighbours(nside, pix, nest=True)

    # get the healpix faces IDs of pix and the neighboring pixels
    _, _, f0 = hp.pix2xyf(nside, pix, nest=True)
    _, _, f  = hp.pix2xyf(nside, n, nest=True)

    # indices which tell get_edge() which edge/verted to return
    # for a given pixel. The default order is compatible with the
    # order returned by hp.get_all_neighbours().
    which = np.arange(8)
    if f0 < 4: # northern hemisphere; 90deg cw rotation for every +1 face increment
        mask = (f < 4)
        which[mask] += 2*(f-f0)[mask]
        which %= 8
    elif f0 >= 8: # southern hemisphere; 90deg ccw rotation for every +1 face increment
        mask = (f >= 8)
        which[mask] -= 2*(f-f0)[mask]
        which %= 8

    # get all edges/vertices 
    # (making sure we skip -1 entries, for pixels with seven neighbors)
    nb = list(get_edge(dk, px, edge) for edge, px in zip(which, n) if px != -1)
    nb = np.concatenate(nb)
    return nb
