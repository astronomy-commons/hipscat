import pytest

from hipscat.pixel_math import HealpixPixel
from hipscat.util import healpix_or_tuple_arg


@healpix_or_tuple_arg
def return_healpix(pixel):
    return pixel


@healpix_or_tuple_arg(parameter_name="some_pixel")
def return_healpix_other_arg(some_arg, some_pixel):
    return some_arg, some_pixel


class ArgTestingClass:
    @healpix_or_tuple_arg
    def return_pixel(self, pixel):
        return pixel

    @staticmethod
    @healpix_or_tuple_arg
    def return_pixel_static(pixel):
        return pixel

    @healpix_or_tuple_arg(parameter_name="some_pixel")
    def return_pixel_other_arg(self, other_arg, some_pixel):
        return other_arg, some_pixel


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


def test_function_can_take_either_argument_at_other_arg_index():
    order = 5
    pixel = 10
    for arg in [HealpixPixel(order, pixel), (order, pixel)]:
        _, returned_pixel = return_healpix_other_arg(None, arg)
        assert isinstance(returned_pixel, HealpixPixel)
        assert returned_pixel.order == order
        assert returned_pixel.pixel == pixel


def test_function_other_args_are_untouched():
    order = 5
    pixel = 10
    test_others = [1, "test", (1, 2)]
    for arg in [HealpixPixel(order, pixel), (order, pixel)]:
        for test_other in test_others:
            other, returned_pixel = return_healpix_other_arg(test_other, arg)
            assert other == test_other
            assert isinstance(returned_pixel, HealpixPixel)
            assert returned_pixel.order == order
            assert returned_pixel.pixel == pixel


def test_method_can_take_either_argument():
    order = 5
    pixel = 10
    obj = ArgTestingClass()
    for arg in [HealpixPixel(order, pixel), (order, pixel)]:
        returned_pixel = obj.return_pixel(arg)
        assert isinstance(returned_pixel, HealpixPixel)
        assert returned_pixel.order == order
        assert returned_pixel.pixel == pixel


def test_static_method_can_take_either_argument():
    order = 5
    pixel = 10
    obj = ArgTestingClass()
    for arg in [HealpixPixel(order, pixel), (order, pixel)]:
        returned_pixel = obj.return_pixel_static(arg)
        assert isinstance(returned_pixel, HealpixPixel)
        assert returned_pixel.order == order
        assert returned_pixel.pixel == pixel


def test_method_can_take_either_argument_at_other_arg_index():
    order = 5
    pixel = 10
    obj = ArgTestingClass()
    for arg in [HealpixPixel(order, pixel), (order, pixel)]:
        _, returned_pixel = obj.return_pixel_other_arg(None, arg)
        assert isinstance(returned_pixel, HealpixPixel)
        assert returned_pixel.order == order
        assert returned_pixel.pixel == pixel


def test_method_other_args_are_untouched():
    order = 5
    pixel = 10
    test_others = [1, "test", (1, 2)]
    obj = ArgTestingClass()
    for arg in [HealpixPixel(order, pixel), (order, pixel)]:
        for test_other in test_others:
            other, returned_pixel = obj.return_pixel_other_arg(test_other, arg)
            assert other == test_other
            assert isinstance(returned_pixel, HealpixPixel)
            assert returned_pixel.order == order
            assert returned_pixel.pixel == pixel
