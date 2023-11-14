"""Utility functions for handling parquet metadata files"""
import tempfile
from typing import List

import pyarrow as pa
import pyarrow.dataset as pds
import pyarrow.parquet as pq

from hipscat.io import file_io, paths
from hipscat.io.file_io.file_pointer import get_fs, strip_leading_slash_for_pyarrow


def row_group_stat_single_value(row_group, stat_key):
    """Convenience method to find the min and max inside a statistics dictionary,
    and raise an error if they're unequal."""
    if stat_key not in row_group.statistics:
        raise ValueError(f"row group doesn't have expected key {stat_key}")
    stat_dict = row_group.statistics[stat_key]
    min_val = stat_dict["min"]
    max_val = stat_dict["max"]
    if min_val != max_val:
        raise ValueError(f"stat min != max ({min_val} != {max_val})")
    return min_val


def write_parquet_metadata(catalog_path, storage_options: dict = None, output_path: str = None):
    """Generate parquet metadata, using the already-partitioned parquet files
    for this catalog

    Args:
        catalog_path (str): base path for the catalog
        storage_options: dictionary that contains abstract filesystem credentials
        output_path (str): base path for writing out metadata files
            defaults to `catalog_path` if unspecified
    """
    ignore_prefixes = [
        "intermediate",
        "_common_metadata",
        "_metadata",
    ]

    dataset = file_io.read_parquet_dataset(
        catalog_path,
        storage_options=storage_options,
        ignore_prefixes=ignore_prefixes,
        exclude_invalid_files=True,
    )
    metadata_collector = []

    for hips_file in dataset.files:
        hips_file_pointer = file_io.get_file_pointer_from_path(hips_file, include_protocol=catalog_path)
        single_metadata = file_io.read_parquet_metadata(hips_file_pointer, storage_options=storage_options)
        relative_path = hips_file[len(catalog_path) :]
        single_metadata.set_file_path(relative_path)
        metadata_collector.append(single_metadata)

    ## Write out the two metadata files
    if output_path is None:
        output_path = catalog_path
    catalog_base_dir = file_io.get_file_pointer_from_path(output_path)
    metadata_file_pointer = paths.get_parquet_metadata_pointer(catalog_base_dir)
    common_metadata_file_pointer = paths.get_common_metadata_pointer(catalog_base_dir)

    file_io.write_parquet_metadata(
        dataset.schema,
        metadata_file_pointer,
        metadata_collector=metadata_collector,
        write_statistics=True,
        storage_options=storage_options,
    )
    file_io.write_parquet_metadata(
        dataset.schema, common_metadata_file_pointer, storage_options=storage_options
    )


def write_parquet_metadata_for_batches(
    batches: List[pa.RecordBatch], output_path: str = None, storage_options: dict = None
):
    """Write parquet metadata files for some pyarrow table batches.
    This writes the batches to a temporary parquet dataset using local storage, and

    Args:
        batches (List[pa.RecordBatch]): create one batch per group of data (partition or row group)
        output_path (str): base path for writing out metadata files
            defaults to `catalog_path` if unspecified
        storage_options: dictionary that contains abstract filesystem credentials
    """

    temp_info_table = pa.Table.from_batches(batches)

    with tempfile.TemporaryDirectory() as temp_pq_file:
        pq.write_to_dataset(temp_info_table, temp_pq_file)
        write_parquet_metadata(temp_pq_file, storage_options=storage_options, output_path=output_path)


def read_row_group_fragments(metadata_file, storage_options: dict = None):
    """Generator for metadata fragment row groups in a parquet metadata file.

    Args:
        metadata_file (str): path to `_metadata` file.
        storage_options: dictionary that contains abstract filesystem credentials
    """
    file_system, dir_pointer = get_fs(file_pointer=metadata_file, storage_options=storage_options)
    dir_pointer = strip_leading_slash_for_pyarrow(dir_pointer, file_system.protocol)
    dataset = pds.parquet_dataset(dir_pointer, filesystem=file_system)

    for frag in dataset.get_fragments():
        for row_group in frag.row_groups:
            yield row_group
