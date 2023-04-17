from __future__ import annotations

import inspect
from functools import wraps

from hipscat.pixel_math import HealpixPixel


def healpix_or_tuple_arg(function=None, *, parameter_name: str = "pixel"):
    """Decorator applied to functions that allows a `HealpixPixel` type argument to also accept
    tuples of (order, pixel)

    The parameter name specified (default: "pixel") is checked for its type. If it is a tuple, it
    is converted into a `HealpixPixel` object and the original function is called with it.

    Args:
        parameter_name: the name of the parameter in the function to check and convert to
            a `HealpixPixel` object
    """

    def construct_new_func(func):
        if parameter_name not in inspect.signature(func).parameters:
            raise ValueError(
                f"Parameter {parameter_name} not in function signature. Specify parameter name of "
                f"HealpixPixel parameter using the decorator with the `parameter_name` property"
            )
        parameter_index = -1
        for index, parameter in enumerate(inspect.signature(func).parameters.keys()):
            if parameter == parameter_name:
                parameter_index = index
                break

        @wraps(func)  # copies func docstring and name
        def accept_multiple_func(*args, **kwargs):
            if len(args) > parameter_index:
                pixel_or_tuple = args[parameter_index]
            else:
                pixel_or_tuple = kwargs[parameter_name]
            if isinstance(pixel_or_tuple, tuple):
                if len(pixel_or_tuple) != 2:
                    raise ValueError(
                        "Tuple must contain two values: HEALPix order and HEALPix pixel number"
                    )
                pixel = HealpixPixel(order=pixel_or_tuple[0], pixel=pixel_or_tuple[1])
                if len(args) > parameter_index:
                    new_args = (
                        args[:parameter_index] + (pixel,) + args[parameter_index + 1 :]
                    )
                    return func(*new_args, **kwargs)
                kwargs[parameter_name] = pixel
                return func(*args, **kwargs)
            if isinstance(pixel_or_tuple, HealpixPixel):
                return func(*args, **kwargs)
            raise TypeError(
                f"Parameter {parameter_name} must either be of type"
                f" `HealpixPixel` or tuple (order, pixel)"
            )

        return accept_multiple_func

    # Applied as a decorator directly
    if function is not None:
        return construct_new_func(function)

    return construct_new_func
