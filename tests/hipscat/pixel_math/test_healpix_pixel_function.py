import numpy as np
import numpy.testing as npt

from hipscat.pixel_math.healpix_pixel_function import get_pixel_argsort


def test_get_pixel_argsort(pixel_list_norder_major, pixel_list_sky_sorting):
    argsort = get_pixel_argsort(pixel_list_norder_major)
    npt.assert_array_equal(argsort, [6, 7, 8, 1, 2, 0, 3, 4, 5])
    sorted_pixel_list = np.array(pixel_list_norder_major)[argsort]
    npt.assert_array_equal(sorted_pixel_list, pixel_list_sky_sorting)
