from __future__ import annotations

from typing import List, TYPE_CHECKING

from hipscat.pixel_math import HealpixInputTypes, get_healpix_pixel
from hipscat.pixel_tree.pixel_node_type import PixelNodeType

if TYPE_CHECKING:
    from hipscat.pixel_tree.pixel_tree import PixelTree


class PixelNode:
    """A node in the HiPSCat quadtree of HEALPix pixels

    Attributes:
        node_type: If the node is a leaf, root, or inner type
        parent: The parent pixel node in the tree
        children: The child nodes of the pixel
    """

    def __init__(
        self,
        pixel: HealpixInputTypes,
        node_type: PixelNodeType,
        tree: PixelTree,
    ) -> None:
        """Inits PixelNode with its attributes

        Raises:
            ValueError: Invalid arguments for the specified pixel type
        """

        pixel = get_healpix_pixel(pixel)

        self.tree = tree

        if node_type == PixelNodeType.ROOT:
            if pixel.order != -1:
                raise ValueError("Root node must be at order -1")

        if node_type in (PixelNodeType.INNER, PixelNodeType.LEAF):
            if pixel.order < 0 or pixel.pixel < 0:
                raise ValueError("Inner and leaf nodes must have an order and pixel number >= 0")

        self.pixel = pixel
        self.node_type = node_type

    def __str__(self) -> str:
        return f"{self.node_type} Order: {self.pixel.order}, Pixel: {self.pixel.pixel}"

    def __repr__(self):
        return self.__str__()

    @property
    def hp_order(self):
        """The order of the HealpixPixel the node is at"""
        return self.pixel.order

    @property
    def hp_pixel(self):
        """The pixel number in NESTED ordering of the HealpixPixel the node is at"""
        return self.pixel.pixel

    @property
    def parent(self) -> PixelNode:
        return self.tree.get_parent_node(self.pixel)

    @property
    def children(self) -> List[PixelNode]:
        return self.tree.get_child_nodes(self.pixel)

    def get_all_leaf_descendants(self) -> List[PixelNode]:
        """Gets all descendant nodes that are leaf nodes.

        Leafs nodes correspond to pixels that have data files containing astronomical objects, so
        this method is used to get the files containing all astronomical objects within the pixel.

        This function called on a leaf node returns a list including the node itself and only itself

        Returns:
            A list containing all leaf nodes that descend from the current node
        """

        leaf_descendants = []
        self._add_all_leaf_descendants_rec(leaf_descendants)
        return leaf_descendants

    def _add_all_leaf_descendants_rec(self, leaf_descendants: List[PixelNode]):
        """Recursively add all leaf descendants to list

        list must be created outside function, done for efficiency vs list concat
        """
        if self.node_type == PixelNodeType.LEAF:
            leaf_descendants.append(self)

        for child in self.children:
            # pylint: disable=protected-access
            child._add_all_leaf_descendants_rec(leaf_descendants)
