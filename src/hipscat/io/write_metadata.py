"""Utility functions for writing metadata files"""

from __future__ import annotations

import dataclasses
import json
from datetime import datetime
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from upath import UPath

from hipscat.io import file_io, paths
from hipscat.pixel_math.healpix_pixel import HealpixPixel


class HipscatEncoder(json.JSONEncoder):
    """Special json encoder for types commonly encountered with hipscat.

    NB: This will only be used by JSON encoding when encountering a type
    that is unhandled by the default encoder.
    """

    def default(self, o):
        if isinstance(o, Path):
            return str(o)
        if isinstance(o, (type, np.dtype, pd.core.dtypes.base.ExtensionDtype)):
            return str(o)
        if isinstance(o, HealpixPixel):
            return str(o)
        if np.issubdtype(o.dtype, np.integer):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)  # pragma: no cover


def write_json_file(metadata_dictionary: dict, file_pointer: str | Path | UPath):
    """Convert metadata_dictionary to a json string and print to file.

    Args:
        metadata_dictionary (:obj:`dictionary`): a dictionary of key-value pairs
        file_pointer (str): destination for the json file
    """
    dumped_metadata = json.dumps(metadata_dictionary, indent=4, cls=HipscatEncoder)
    file_io.write_string_to_file(file_pointer, dumped_metadata + "\n")


def write_catalog_info(catalog_base_dir, dataset_info):
    """Write a catalog_info.json file with catalog metadata

    Args:
        catalog_base_dir (str): base directory for catalog, where file will be written
        dataset_info (:obj:`BaseCatalogInfo`) base metadata for the catalog
    """
    metadata = dataclasses.asdict(dataset_info)
    catalog_info_pointer = paths.get_catalog_info_pointer(catalog_base_dir)

    write_json_file(metadata, catalog_info_pointer)


def write_provenance_info(catalog_base_dir: str | Path | UPath, dataset_info, tool_args: dict):
    """Write a provenance_info.json file with all assorted catalog creation metadata

    Args:
        catalog_base_dir (str): base directory for catalog, where file will be written
        dataset_info (:obj:`BaseCatalogInfo`) base metadata for the catalog
        tool_args (:obj:`dict`): dictionary of additional arguments provided by the tool creating
            this catalog.
    """
    metadata = dataclasses.asdict(dataset_info)
    metadata["version"] = version("hipscat")
    now = datetime.now()
    metadata["generation_date"] = now.strftime("%Y.%m.%d")

    metadata["tool_args"] = tool_args

    metadata_pointer = paths.get_provenance_pointer(catalog_base_dir)
    write_json_file(metadata, metadata_pointer)


def write_partition_info(catalog_base_dir: str | Path | UPath, destination_healpix_pixel_map: dict):
    """Write all partition data to CSV file.

    Args:
        catalog_base_dir (str): base directory for catalog, where file will be written
        destination_healpix_pixel_map (dict):  dictionary that maps the HealpixPixel to a
            tuple of origin pixel information:

                - 0 - the total number of rows found in this destination pixel
                - 1 - the set of indexes in histogram for the pixels at the original healpix order
    """
    partition_info_pointer = paths.get_partition_info_pointer(catalog_base_dir)
    data_frame = pd.DataFrame(destination_healpix_pixel_map.keys())
    # Set column names.
    data_frame.columns = [
        "Norder",
        "Npix",
    ]
    data_frame["num_rows"] = [pixel_info[0] for pixel_info in destination_healpix_pixel_map.values()]
    data_frame["Dir"] = [int(x / 10_000) * 10_000 for x in data_frame["Npix"]]

    # Reorder the columns to match full path, and force to integer types.
    data_frame = data_frame[["Norder", "Dir", "Npix", "num_rows"]].astype(int)

    file_io.write_dataframe_to_csv(data_frame, partition_info_pointer, index=False)


def write_fits_map(catalog_path, histogram: np.ndarray):
    """Write the object spatial distribution information to a healpix FITS file.

    Args:
        catalog_path (str): base path for the catalog
        histogram (:obj:`np.ndarray`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
    """
    catalog_base_dir = file_io.get_upath(catalog_path)
    map_file_pointer = paths.get_point_map_file_pointer(catalog_base_dir)
    file_io.write_fits_image(histogram, map_file_pointer)
