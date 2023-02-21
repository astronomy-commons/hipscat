import pytest


@pytest.fixture
def matching_nested_pixels_1():
    return [
        {"order": 0, "pixel": 0},
        {"order": 1, "pixel": 1},
        {"order": 2, "pixel": 4},
        {"order": 3, "pixel": 16},
        {"order": 4, "pixel": 64},
        {"order": 5, "pixel": 256},
    ]


@pytest.fixture
def matching_nested_pixels_2():
    return [
        {"order": 0, "pixel": 2},
        {"order": 1, "pixel": 8},
        {"order": 2, "pixel": 32},
        {"order": 3, "pixel": 128},
        {"order": 4, "pixel": 512},
        {"order": 5, "pixel": 2048},
    ]
