"""Utility functions for writing metadata files"""

import json
from datetime import datetime
from importlib.metadata import version

import numpy as np
import pandas as pd
import pyarrow.dataset as pds

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
    file_io.write_string_to_file(file_pointer, dumped_metadata + "\n")


def write_catalog_info(catalog_parameters, histogram: np.ndarray):
    """Write a catalog_info.json file with catalog metadata

    Args:
        catalog_parameters (:obj:`CatalogParameters`): collection of runtime arguments for
            the new catalog
        histogram (:obj:`np.ndarray`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
    """
    metadata = {}
    metadata["catalog_name"] = catalog_parameters.catalog_name
    metadata["version"] = version("hipscat")
    now = datetime.now()
    metadata["generation_date"] = now.strftime("%Y.%m.%d")
    metadata["epoch"] = catalog_parameters.epoch
    metadata["ra_kw"] = catalog_parameters.ra_column
    metadata["dec_kw"] = catalog_parameters.dec_column
    metadata["id_kw"] = catalog_parameters.id_column
    metadata["total_objects"] = histogram.sum()

    metadata["origin_healpix_order"] = catalog_parameters.highest_healpix_order
    metadata["pixel_threshold"] = catalog_parameters.pixel_threshold

    catalog_info_pointer = paths.get_catalog_info_pointer(
        catalog_parameters.catalog_base_dir
    )
    write_json_file(metadata, catalog_info_pointer)


def write_provenance_info(catalog_parameters, tool_args):
    """Write a provenance_info.json file with all assorted catalog creation metadata

    Args:
        catalog_parameters (:obj:`CatalogParameters`): collection of runtime arguments
            for the new catalog
        tool_args (:obj:`dict`): dictionary of additional arguments provided by the tool creating
            this catalog.
    """
    metadata = {}
    metadata["catalog_name"] = catalog_parameters.catalog_name
    metadata["version"] = version("hipscat")
    now = datetime.now()
    metadata["generation_date"] = now.strftime("%Y.%m.%d")
    metadata["epoch"] = catalog_parameters.epoch
    metadata["ra_kw"] = catalog_parameters.ra_column
    metadata["dec_kw"] = catalog_parameters.dec_column
    metadata["id_kw"] = catalog_parameters.id_column

    metadata["origin_healpix_order"] = catalog_parameters.highest_healpix_order
    metadata["pixel_threshold"] = catalog_parameters.pixel_threshold

    metadata["tool_args"] = tool_args

    metadata_pointer = paths.get_provenance_pointer(catalog_parameters.catalog_base_dir)
    write_json_file(metadata, metadata_pointer)


def write_partition_info(catalog_parameters, destination_pixel_map: dict):
    """Write all partition data to CSV file.

    Args:
        catalog_parameters (:obj:`CatalogParameters`): collection of runtime arguments for
            the new job
        destination_pixel_map (dict): data frame that has as columns:

            - pixel order of destination
            - pixel number of destination
            - sum of rows in destination
            - list of all source pixels at original order
    """
    partition_info_pointer = paths.get_partition_info_pointer(
        catalog_parameters.catalog_base_dir
    )
    data_frame = pd.DataFrame(destination_pixel_map.keys())

    data_frame.columns = [
        "Norder",
        "Npix",
        "num_objects",
    ]
    data_frame["Dir"] = int(data_frame["Npix"] / 10_000) * 10_000

    data_frame = data_frame[
        [
            "Norder",
            "Dir",
            "Npix",
            "num_objects",
        ]
    ].astype(int)

    file_io.write_dataframe_to_csv(data_frame, partition_info_pointer, index=False)


def write_legacy_metadata(
    catalog_parameters, histogram: np.ndarray, pixel_map: np.ndarray
):
    """Write a <catalog_name>_meta.json with the format expected by the prototype catalog.

    Args:
        catalog_parameters (:obj:`CatalogParameters`): collection of runtime arguments for
            the new catalog
        histogram (:obj:`np.ndarray`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
        pixel_map (:obj:`np.ndarray`): one-dimensional numpy array of integer 3-tuples.
            See :func:`~hipscat.pixel_math.partition_stats.generate_alignment` for more
            details on this format.
    """
    metadata = {}
    metadata["cat_name"] = catalog_parameters.catalog_name
    metadata["ra_kw"] = catalog_parameters.ra_column
    metadata["dec_kw"] = catalog_parameters.dec_column
    metadata["id_kw"] = catalog_parameters.id_column
    metadata["n_sources"] = histogram.sum()
    metadata["pix_threshold"] = catalog_parameters.pixel_threshold
    metadata["urls"] = catalog_parameters.input_paths

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
        catalog_parameters.catalog_base_dir,
        f"{catalog_parameters.catalog_name}_meta.json",
    )

    write_json_file(metadata, metadata_pointer)


def write_parquet_metadata(catalog_path):
    """Generate parquet metadata, using the already-partitioned parquet files
    for this catalog

    Args:
        catalog_path (str): base path for the catalog
    """

    dataset = pds.dataset(catalog_path, format="parquet", exclude_invalid_files=True)
    metadata_collector = []

    for hips_file in dataset.files:
        hips_file_pointer = file_io.get_file_pointer_from_path(hips_file)
        single_metadata = file_io.read_parquet_metadata(hips_file_pointer)
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
        catalog_parameters (:obj:`CatalogParameters`): collection of runtime arguments for
            the new catalog
        histogram (:obj:`np.ndarray`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
    """
    catalog_base_dir = file_io.get_file_pointer_from_path(catalog_path)
    map_file_pointer = paths.get_point_map_file_pointer(catalog_base_dir)
    file_io.write_fits_image(histogram, map_file_pointer)
