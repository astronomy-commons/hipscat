import cProfile

from hipscat.pixel_tree.pixel_alignment import align_trees
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder
import random

if __name__ == '__main__':
    pixels_a = [(8, i) for i in range(0, 700000, 3)]
    random.shuffle(pixels_a)
    pixels_b = [(10, i) for i in range(0, 12000000, 50)]
    random.shuffle(pixels_b)
    a = PixelTreeBuilder.from_healpix(pixels_a)
    b = PixelTreeBuilder.from_healpix(pixels_b)
    with cProfile.Profile() as pr:
        align_trees(a, b, alignment_type='outer')
        pr.dump_stats("treeprofile2.pstat")
