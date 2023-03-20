"""Utility functions for writing metadata files"""

import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
from setuptools_scm import get_version

from hipscat.io import file_io, paths


class NumpyEncoder(json.JSONEncoder):
    """Special json encoder for numpy integer types"""

    def default(self, o):
        int_object = o
        if isinstance(int_object, (np.int64, np.ulonglong)):
            return int(int_object)
        return o


def write_json_file(metadata_dictionary: dict, file_pointer: file_io.FilePointer):
    """Convert metadata_dictionary to a json string and print to file.

    Args:
        metadata_dictionary (:obj:`dictionary`): a dictionary of key-value pairs
        file_pointer (str): destination for the json file
    """
    dumped_metadata = json.dumps(metadata_dictionary, indent=4, cls=NumpyEncoder)
    file_io.write_string_to_file(file_pointer, dumped_metadata)


def write_catalog_info(catalog_parameters, histogram: np.ndarray):
    """Write a catalog_info.json file with catalog metadata

    Args:
        catalog_parameters (:obj:`CatalogParameters`): collection of runtime arguments for the partitioning job
        histogram (:obj:`np.ndarray`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
    """
    metadata = {}
    metadata["catalog_name"] = catalog_parameters.catalog_name
    metadata["version"] = get_version()
    now = datetime.now()
    metadata["generation_date"] = now.strftime("%Y.%m.%d")
    metadata["epoch"] = catalog_parameters.epoch
    metadata["ra_kw"] = catalog_parameters.ra_column
    metadata["dec_kw"] = catalog_parameters.dec_column
    metadata["id_kw"] = catalog_parameters.id_column
    metadata["total_objects"] = histogram.sum()

    metadata["origin_healpix_order"] = catalog_parameters.highest_healpix_order
    metadata["pixel_threshold"] = catalog_parameters.pixel_threshold

    catalog_info_pointer = paths.get_catalog_info_pointer(catalog_parameters.catalog_base_dir)
    write_json_file(metadata, catalog_info_pointer)


def write_partition_info(catalog_parameters, destination_pixel_map: dict):
    """Write all partition data to CSV file.

    Args:
        catalog_parameters (:obj:`CatalogParameters`): collection of runtime arguments for the partitioning job
        destination_pixel_map (dict): data frame that has as columns:

            - pixel order of destination
            - pixel number of destination
            - sum of rows in destination
            - list of all source pixels at original order
    """
    partition_info_pointer = paths.get_partition_info_pointer(catalog_parameters.catalog_base_dir)
    data_frame = pd.DataFrame(destination_pixel_map.keys())
    data_frame.columns = ["order", "pixel", "num_objects"]
    data_frame = data_frame.astype(int)
    file_io.write_dataframe_to_csv(data_frame, partition_info_pointer, index=False)


def write_legacy_metadata(catalog_patameters, histogram: np.ndarray, pixel_map: np.ndarray):
    """Write a <catalog_name>_meta.json with the format expected by the prototype catalog.

    Args:
        catalog_patameters (:obj:`CatalogParameters`): collection of runtime arguments for the partitioning job
        histogram (:obj:`np.ndarray`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
        pixel_map (:obj:`np.ndarray`): one-dimensional numpy array of integer 3-tuples.
            See :func:`~hipscat.pixel_math.partition_stats.generate_alignment` for more
            details on this format.
    """
    metadata = {}
    metadata["cat_name"] = catalog_patameters.catalog_name
    metadata["ra_kw"] = catalog_patameters.ra_column
    metadata["dec_kw"] = catalog_patameters.dec_column
    metadata["id_kw"] = catalog_patameters.id_column
    metadata["n_sources"] = histogram.sum()
    metadata["pix_threshold"] = catalog_patameters.pixel_threshold
    metadata["urls"] = catalog_patameters.input_paths

    hips_structure = {}
    temp = [i for i in pixel_map if i is not None]
    unique_partitions = np.unique(temp, axis=0)
    for item in unique_partitions:
        order = int(item[0])
        pixel = int(item[1])
        if order not in hips_structure:
            hips_structure[order] = []
        hips_structure[order].append(pixel)

    metadata["hips"] = hips_structure

    metadata_pointer = file_io.append_paths_to_pointer(
        catalog_patameters.catalog_base_dir,
        f"{catalog_patameters.catalog_name}_meta.json"
    )

    write_json_file(metadata, metadata_pointer)
