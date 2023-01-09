"""Utility functions for writing metadata files"""

import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
import pkg_resources


class NumpyEncoder(json.JSONEncoder):
    """Special json encoder for numpy integer types"""

    def default(self, o):
        int_object = o
        if isinstance(int_object, (np.int64, np.ulonglong)):
            return int(int_object)


def write_json_file(metadata_dictionary, file_name):
    """Convert metadata_dictionary to a json string and print to file.
    Args:
        metadata_dictionary (:obj:`dictionary`): a dictionary of key-value pairs
        file_name (str): destination for the json file
    """
    dumped_metadata = json.dumps(metadata_dictionary, indent=4, cls=NumpyEncoder)
    with open(
        file_name,
        "w",
        encoding="utf-8",
    ) as metadata_file:
        metadata_file.write(dumped_metadata + "\n")


def write_catalog_info(args, histogram):
    """Write a catalog_info.json file with catalog metadata

    Args:
        args (:obj:`PartitionArguments`): collection of runtime arguments for the partitioning job
        histogram (:obj:`np.array`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
    """
    metadata = {}
    metadata["catalog_name"] = args.catalog_name
    metadata["version"] = pkg_resources.get_distribution("lsd2").version
    now = datetime.now()
    metadata["generation_date"] = now.strftime("%Y.%m.%d")
    metadata["ra_kw"] = args.ra_column
    metadata["dec_kw"] = args.dec_column
    metadata["id_kw"] = args.id_column
    metadata["total_objects"] = histogram.sum()

    metadata["origin_healpix_order"] = args.highest_healpix_order
    metadata["pixel_threshold"] = args.pixel_threshold

    metadata_filename = os.path.join(args.catalog_path, "catalog_info.json")
    write_json_file(metadata, metadata_filename)


def write_partition_info(args, destination_pixel_map):
    """Write all partition data to CSV file.
    Args:
        args (:obj:`PartitionArguments`): collection of runtime arguments for the partitioning job
        destination_pixel_map (:obj:`DataFrame`)
          data frame that has as columns:
          - pixel order of destination
          - pixel number of destination
          - sum of rows in destination
          - list of all source pixels at original order
    """
    metadata_filename = os.path.join(args.catalog_path, "partition_info.csv")
    data_frame = pd.DataFrame(destination_pixel_map.keys())
    data_frame.columns = ["order", "pixel", "num_objects"]
    data_frame.to_csv(metadata_filename, index=False)


def write_legacy_metadata(args, histogram, pixel_map):
    """Write a <catalog_name>_meta.json with the format expected by the prototype catalog.

    Args:
        args (:obj:`PartitionArguments`): collection of runtime arguments for the partitioning job
        histogram (:obj:`np.array`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
        pixel_map (:obj:`np.array`): one-dimensional numpy array of integer 3-tuples.
            See `histogram.generate_alignment` for more details on this format.
    """
    metadata = {}
    metadata["cat_name"] = args.catalog_name
    metadata["ra_kw"] = args.ra_column
    metadata["dec_kw"] = args.dec_column
    metadata["id_kw"] = args.id_column
    metadata["n_sources"] = histogram.sum()
    metadata["pix_threshold"] = args.pixel_threshold
    metadata["urls"] = args.input_paths

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

    metadata_filename = os.path.join(
        args.catalog_path, f"{args.catalog_name}_meta.json"
    )
    write_json_file(metadata, metadata_filename)
