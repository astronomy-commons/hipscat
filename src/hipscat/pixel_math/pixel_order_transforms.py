from typing import List, Tuple


def calculate_lower_order_hp_pixel(
    order: int, pixel: int, delta_order: int = 1
) -> (int, int):
    """Calculate the HEALPix pixel at a lower order that contains a given pixel

    For example, used to calculate the pixel at order 2 that contains the pixel at order 3, pixel 34

    Args:
        order: HEALPix order of pixel
        pixel: HEALPix pixel number, in nested ordering scheme
        delta_order: difference in order for the calculated pixel, default = 1

    Returns:
        The tuple (order, pixel) of the calculated pixel at the lower order
    """

    if delta_order > order:
        raise ValueError("Calculated pixel order must be greater than 0")

    new_order = order - delta_order
    new_pixel = pixel >> (2 * delta_order)
    return new_order, new_pixel


def calculate_higher_order_hp_pixels(
    order: int, pixel: int, delta_order: int = 1
) -> List[Tuple[int, int]]:
    """Calculate the HEALPix pixels at a higher order that are contained by a given pixel

    For example, used to calculate the pixels at order 3 that are within pixel 10, order 2

    Args:
        order: HEALPix order of pixel
        pixel: HEALPix pixel number, in nested ordering scheme
        delta_order: difference in order for the calculated pixels, default = 1

    Returns:
        A list of tuples (order, pixel) of the calculated pixels at the higher order
    """

    pixels = []
    new_order = order + delta_order
    for new_pixel in range(
        pixel << (2 * delta_order), (pixel + 1) << (2 * delta_order)
    ):
        pixels.append((new_order, new_pixel))
    return pixels
