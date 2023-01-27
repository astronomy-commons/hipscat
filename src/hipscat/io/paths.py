"""Methods for creating partitioned data paths"""

import os


def pixel_directory(catalog_path="", pixel_order=0, pixel_number=0):
    """Create path *string* for a pixel directory. This will not create the directory.

    The directory name will take the form of:

        <catalog_path>/Norder<pixel_order>/Npix<pixel_number>/

    Args:
        catalog_path (str): base directory of the catalog (includes catalog name)
        pixel_order (int): the healpix order of the pixel
        pixel_number (int): the healpix pixel
    Returns:
        string directory name
    """
    return os.path.join(
        catalog_path, f"Norder{int(pixel_order)}/Npix{int(pixel_number)}"
    )


def pixel_catalog_file(catalog_path="", pixel_order=0, pixel_number=0):
    """Create path *string* for a pixel catalog file. This will not create the directory or file.

    The catalog file name will take the form of:

        <catalog_path>/Norder<pixel_order>/Npix<pixel_number>/catalog.parquet

    Args:
        catalog_path (str): base directory of the catalog (includes catalog name)
        pixel_order (int): the healpix order of the pixel
        pixel_number (int): the healpix pixel
    Returns:
        string catalog file name
    """
    return os.path.join(
        catalog_path,
        f"Norder{int(pixel_order)}/Npix{int(pixel_number)}",
        "catalog.parquet",
    )
