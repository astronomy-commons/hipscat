from hipscat.pixel_tree import align_trees, PixelAlignmentType
from hipscat.pixel_tree.pixel_tree import PixelTree


def compute_negative_tree_pixels(tree: PixelTree):
    tree_pixels = set(tree.get_healpix_pixels())
    full_tree = PixelTree.from_healpix([(0, i) for i in range(12)])
    alignment = align_trees(full_tree, tree, alignment_type=PixelAlignmentType.OUTER)
    aligned_tree = alignment.pixel_tree
    return [p for p in aligned_tree.get_healpix_pixels() if p not in tree_pixels]
