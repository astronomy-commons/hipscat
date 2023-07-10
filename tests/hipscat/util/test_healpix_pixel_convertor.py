import pytest

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_math.healpix_pixel_convertor import HealpixInputTypes, get_healpix_pixel


def return_healpix(pixel: HealpixInputTypes):
    return get_healpix_pixel(pixel)


def test_function_can_take_either_argument():
    order = 5
    pixel = 10
    for arg in [HealpixPixel(order, pixel), (order, pixel)]:
        returned_pixel = return_healpix(arg)
        assert isinstance(returned_pixel, HealpixPixel)
        assert returned_pixel.order == order
        assert returned_pixel.pixel == pixel


def test_function_raises_error_for_wrong_type():
    with pytest.raises(TypeError):
        return_healpix("test")


def test_function_raises_error_for_wrong_size_tuple():
    with pytest.raises(ValueError):
        return_healpix((1, 2, 3))
