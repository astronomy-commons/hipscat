"""Utility functions for writing metadata files"""

import dataclasses
import json
from datetime import datetime
from importlib.metadata import version

import numpy as np
import pandas as pd
import pyarrow.dataset as pds

from hipscat.io import file_io, paths


def write_json_file(metadata_dictionary: dict, file_pointer: file_io.FilePointer):
    """Convert metadata_dictionary to a json string and print to file.

    Args:
        metadata_dictionary (:obj:`dictionary`): a dictionary of key-value pairs
        file_pointer (str): destination for the json file
    """
    dumped_metadata = json.dumps(metadata_dictionary, indent=4)
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


def write_provenance_info(catalog_base_dir: file_io.FilePointer, dataset_info, tool_args: dict):
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


def write_partition_info(
    catalog_base_dir: file_io.FilePointer,
    destination_healpix_pixel_map: dict,
):
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
    data_frame = data_frame[
        [
            "Norder",
            "Dir",
            "Npix",
            "num_rows",
        ]
    ].astype(int)

    file_io.write_dataframe_to_csv(data_frame, partition_info_pointer, index=False)


def write_parquet_metadata(catalog_path):
    """Generate parquet metadata, using the already-partitioned parquet files
    for this catalog

    Args:
        catalog_path (str): base path for the catalog
    """

    dataset = pds.dataset(
        catalog_path,
        format="parquet",
        exclude_invalid_files=True,
        ignore_prefixes=["intermediate", "_common_metadata", "_metadata"],
    )
    metadata_collector = []

    for hips_file in dataset.files:
        hips_file_pointer = file_io.get_file_pointer_from_path(hips_file)
        single_metadata = file_io.read_parquet_metadata(hips_file_pointer)
        relative_path = hips_file[len(catalog_path) :]
        single_metadata.set_file_path(relative_path)
        metadata_collector.append(single_metadata)

    ## Write out the two metadata files
    catalog_base_dir = file_io.get_file_pointer_from_path(catalog_path)
    metadata_file_pointer = paths.get_parquet_metadata_pointer(catalog_base_dir)
    common_metadata_file_pointer = paths.get_common_metadata_pointer(catalog_base_dir)

    file_io.write_parquet_metadata(
        dataset.schema, metadata_file_pointer, metadata_collector=metadata_collector
    )
    file_io.write_parquet_metadata(dataset.schema, common_metadata_file_pointer)


def write_fits_map(catalog_path, histogram: np.ndarray):
    """Write the object spatial distribution information to a healpix FITS file.

    Args:
        catalog_path (str): base path for the catalog
        histogram (:obj:`np.ndarray`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
    """
    catalog_base_dir = file_io.get_file_pointer_from_path(catalog_path)
    map_file_pointer = paths.get_point_map_file_pointer(catalog_base_dir)
    file_io.write_fits_image(histogram, map_file_pointer)
