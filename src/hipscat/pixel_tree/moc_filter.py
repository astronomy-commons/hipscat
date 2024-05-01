import numba
import numpy as np
from mocpy import MOC
from numba import njit

from hipscat.pixel_tree.pixel_tree import PixelTree


def filter_by_moc(
    tree: PixelTree,
    moc: MOC,
) -> PixelTree:
    moc_ranges = moc.to_depth29_ranges
    tree_29_ranges = tree.tree << (2 * (29 - tree.tree_order))
    tree_mask = perform_filter_by_moc(tree_29_ranges, moc_ranges)
    return PixelTree(tree.tree[tree_mask], tree.tree_order)


@njit(
    numba.bool_[::1](
        numba.int64[:, :],
        numba.uint64[:, :],
    )
)
def perform_filter_by_moc(
    tree: np.ndarray,
    moc: np.ndarray,
) -> np.ndarray:
    """Performs filtering with lists of pixel intervals"""
    output = np.full(tree.shape[0], fill_value=False, dtype=np.bool_)
    tree_index = 0
    moc_index = 0
    while tree_index < len(tree) and moc_index < len(moc):
        tree_pix = tree[tree_index]
        moc_pix = moc[moc_index]
        if tree_pix[0] >= moc_pix[1]:
            # Don't overlap, tree pixel ahead so move onto next MOC pixel
            moc_index += 1
            continue
        if moc_pix[0] >= tree_pix[1]:
            # Don't overlap, MOC pixel ahead so move onto next tree pixel
            tree_index += 1
            continue
        # Pixels overlap, so include current tree pixel and check next tree pixel
        output[tree_index] = True
        tree_index += 1
    return output
