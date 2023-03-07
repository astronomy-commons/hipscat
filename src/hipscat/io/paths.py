"""Methods for creating partitioned data paths"""

import os


def pixel_directory(
    catalog_path="", pixel_order=0, pixel_number=None, directory_number=None
):
    """Create path *string* for a pixel directory. This will not create the directory.

    One of pixel_number or directory_number is required. The directory name will
    take the HiPS standard form of:

        <catalog_path>/Norder=<pixel_order>/Dir=<directory number>

    Where the directory number is calculated using integer division as:

        (pixel_number/10000)*10000

    Args:
        catalog_path (str): base directory of the catalog (includes catalog name)
        pixel_order (int): the healpix order of the pixel
        directory_number (int): directory number
        pixel_number (int): the healpix pixel
    Returns:
        string directory name
    """
    norder = int(pixel_order)
    if pixel_number is None and directory_number is None:
        raise ValueError(
            "One of pixel_number or directory_number is required to create pixel directory"
        )
    if directory_number is not None:
        ndir = directory_number
    else:
        npix = int(pixel_number)
        ndir = int(npix / 10_000) * 10_000
    return os.path.join(catalog_path, f"Norder={norder}/Dir={ndir}")


def pixel_catalog_file(catalog_path="", pixel_order=0, pixel_number=0):
    """Create path *string* for a pixel catalog file. This will not create the directory or file.

    The catalog file name will take the HiPS standard form of:

        <catalog_path>/Norder=<pixel_order>/Dir=<directory number>/Npix=<pixel_number>.parquet

    Where the directory number is calculated using integer division as:

        (pixel_number/10000)*10000

    Args:
        catalog_path (str): base directory of the catalog (includes catalog name)
        pixel_order (int): the healpix order of the pixel
        directory_number (int): directory number
        pixel_number (int): the healpix pixel
    Returns:
        string catalog file name
    """
    norder = int(pixel_order)
    npix = int(pixel_number)
    ndir = int(npix / 10_000) * 10_000
    return os.path.join(
        catalog_path,
        f"Norder={norder}/Dir={ndir}/Npix={npix}.parquet",
    )
