"""Generate a molleview map with the pixel densities of the catalog"""

import time

import healpy as hp
import numpy as np
from matplotlib import pyplot as plt

from hipscat.catalog import Catalog


def run():
    """Load a catalog from the indicated path, and create a molleview map."""
    start = time.perf_counter()

    ## *********************************************************
    ##  HEY! Change this path!
    ## *********************************************************
    catalog = Catalog("/home/delucchi/xmatch/catalogs/td_demo")

    pixels = catalog.get_pixels()

    catalog_orders = pixels.order.unique()
    catalog_orders.sort()
    max_order = catalog_orders[-1]

    order_map = np.full(hp.order2npix(max_order), hp.pixelfunc.UNSEEN)

    for _, pixel in pixels.iterrows():
        explosion_factor = 4 ** (max_order - pixel.order)
        exploded_pixels = [
            *range(pixel.pixel * explosion_factor, (pixel.pixel + 1) * explosion_factor)
        ]
        order_map[exploded_pixels] = pixel.order

    end = time.perf_counter()
    print(f"Elapsed time: {int(end-start)} sec")

    hp.mollview(order_map, max=max_order, title="Catalog density map", nest=True)
    plt.show()


if __name__ == "__main__":
    run()
