"""Tests of molleview plot functionality"""


import matplotlib.pyplot as plt

from hipscat.catalog import Catalog
from hipscat.inspection import visualize_pixels


def test_show_plot(small_sky_dir):
    """Test that a plot is generated"""

    cat = Catalog(small_sky_dir)
    visualize_pixels.plot_pixels(cat)
    plt.show()
    