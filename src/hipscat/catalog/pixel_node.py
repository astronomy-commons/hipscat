from __future__ import annotations

from typing import List

from hipscat.catalog.pixel_node_type import PixelNodeType


class PixelNode:
    """A node in the HIPSCat quadtree of HEALPix pixels

    Attributes:
        hp_order: HEALPix order of the pixel
        hp_pixel: HEALPix pixel number
        node_type: If the node is a leaf, root, or inner type
        parent: The parent pixel node in the tree
        children: The child nodes of the pixel

    """

    def __init__(self,
                 hp_order: int | None,
                 hp_pixel: int | None,
                 node_type: PixelNodeType,
                 parent: PixelNode | None = None,
                 children: List[PixelNode] = None):
        """Inits PixelNode with its attributes

        Raises:
            ValueError: Invalid arguments for the specified pixel type
        """

        if node_type == PixelNodeType.ROOT and parent is not None:
            raise ValueError("Root node cannot have a parent")

        if node_type == PixelNodeType.INNER or node_type == PixelNodeType.LEAF:
            if parent is None:
                raise ValueError("Inner and leaf nodes must have a parent")
            if hp_pixel is None or hp_order is None:
                raise ValueError("Inner and leaf nodes must have an order and pixel number")

        if children is None:
            children = []

        self.hp_order = hp_order
        self.hp_pixel = hp_pixel
        self.node_type = node_type
        self.parent = parent
        self.children = children

        if self.parent is not None:
            self.parent.add_child_node(self)

    def add_child_node(self, child: PixelNode):
        """Adds a child node to the node

        Args:
            child: child to add
        """
        self.children.append(child)

    def get_all_leaf_descendants(self) -> List[PixelNode]:
        """Gets all descendant nodes that are leaf nodes.

        Leafs nodes correspond to pixels that have data files containing astronomical objects, so this method is used
        to get the files containing all astronomical objects within the pixel

        This function called on a leaf node returns a list including the node itself

        Returns:
            A list containing all leaf nodes that descend from the current node and the current node if it is a leaf
        """

        if self.node_type == PixelNodeType.LEAF:
            return [self]

        leaf_descendants = []
        for child in self.children:
            leaf_descendants += child.get_all_leaf_descendants()
        return leaf_descendants
