from hipscat.pixel_math import (calculate_higher_order_hp_pixels,
                                calculate_lower_order_hp_pixel)


def test_calculate_lower_order_hp_pixel(
    matching_nested_pixels_1, matching_nested_pixels_2
):
    lowest_order_pixel_1 = matching_nested_pixels_1[0]
    assert_transformed_pixels_match_lower_order_pixel(
        lowest_order_pixel_1, matching_nested_pixels_1
    )
    lowest_order_pixel_2 = matching_nested_pixels_2[0]
    assert_transformed_pixels_match_lower_order_pixel(
        lowest_order_pixel_2, matching_nested_pixels_2
    )


def assert_transformed_pixels_match_lower_order_pixel(
    lowest_order_pixel, nested_pixels_to_test
):
    for pixel in nested_pixels_to_test:
        delta_order = pixel["order"] - lowest_order_pixel["order"]
        order, pixel = calculate_lower_order_hp_pixel(**pixel, delta_order=delta_order)
        assert (order, pixel) == (
            lowest_order_pixel["order"],
            lowest_order_pixel["pixel"],
        )


def test_calculate_higher_order_hp_pixel(
    matching_nested_pixels_1, matching_nested_pixels_2
):
    highest_order_pixel_1 = matching_nested_pixels_1[-1]
    assert_transformed_pixels_match_higher_order_pixel(
        highest_order_pixel_1, matching_nested_pixels_1
    )
    highest_order_pixel_2 = matching_nested_pixels_2[-1]
    assert_transformed_pixels_match_higher_order_pixel(
        highest_order_pixel_2, matching_nested_pixels_2
    )


def assert_transformed_pixels_match_higher_order_pixel(
    highest_order_pixel, nested_pixels_to_test
):
    for pixel in nested_pixels_to_test:
        delta_order = highest_order_pixel["order"] - pixel["order"]
        pixels = calculate_higher_order_hp_pixels(**pixel, delta_order=delta_order)
        assert (highest_order_pixel["order"], highest_order_pixel["pixel"]) in pixels
