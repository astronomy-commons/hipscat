from __future__ import annotations

import json
from typing import Any

import healpy as hp
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pyarrow.dataset as pds
import tempfile
import io
from os.path import join as ospathjoin

from hipscat.io.file_io.file_pointer import FilePointer, get_fs


def make_directory(file_pointer: FilePointer, exist_ok: bool = False, storage_options: dict = {}):
    """Make a directory at a given file pointer

    Will raise an error if a directory already exists, unless `exist_ok` is True in which case
    any existing directories will be left unmodified

    Args:
        file_pointer: location in file system to make directory
        exist_ok: Default False. If false will raise error if directory exists. If true existing
            directories will be ignored and not modified
        storage_options: dictionary that contains abstract filesystem credentials

    Raises:
        OSError
    """
    fs, file_pointer = get_fs(file_pointer, storage_options=storage_options)
    fs.makedirs(file_pointer, exist_ok=exist_ok)


def remove_directory(file_pointer: FilePointer, ignore_errors=False, storage_options: dict = {}):
    """Remove a directory, and all contents, recursively.

    Args:
        file_pointer: directory in file system to remove
        ignore_errors: if True errors resulting from failed removals will be ignored
        storage_options: dictionary that contains abstract filesystem credentials
    """

    fs, file_pointer = get_fs(file_pointer, storage_options)
    if ignore_errors:
        try:
            fs.rm(file_pointer, recursive=True)
        except:
            #fsspec doesn't have a "ignore_errors" field in the rm method
            pass    
    else:
        fs.rm(file_pointer, recursive=True)


def write_string_to_file(file_pointer: FilePointer, string: str, encoding: str = "utf-8", storage_options: dict = {}):
    """Write a string to a text file

    Args:
        file_pointer: file location to write file to
        string: string to write to file
        encoding: Default: 'utf-8', encoding method to write to file with
        storage_options: dictionary that contains abstract filesystem credentials
    """
    fs, file_pointer = get_fs(file_pointer, storage_options)
    with fs.open(file_pointer, "w", encoding=encoding) as _file:
        _file.write(string)


def load_text_file(file_pointer: FilePointer, encoding: str = "utf-8", storage_options: dict = {}):
    """Load a json file to a dictionary

    Args:
        file_pointer: location of file to read
        encoding: string encoding method used by the file
        storage_options: dictionary that contains abstract filesystem credentials
    Returns:
        dictionary of key value pairs loaded from the JSON file
    """
    fs, file_pointer = get_fs(file_pointer, storage_options)
    with fs.open(file_pointer, "r", encoding=encoding) as _text_file:
        text_file = _text_file.readlines()

    return text_file


def load_json_file(file_pointer: FilePointer, encoding: str = "utf-8", storage_options: dict = {}) -> dict:
    """Load a json file to a dictionary

    Args:
        file_pointer: location of file to read
        encoding: string encoding method used by the file
        storage_options: dictionary that contains abstract filesystem credentials
    Returns:
        dictionary of key value pairs loaded from the JSON file
    """

    json_dict = None
    fs, file_pointer = get_fs(file_pointer, storage_options)
    with fs.open(file_pointer, "r", encoding=encoding) as json_file:
        json_dict = json.load(json_file)

    return json_dict


def load_csv_to_pandas(file_pointer: FilePointer, storage_options: dict = {}, **kwargs) -> pd.DataFrame:
    """Load a csv file to a pandas dataframe

    Args:
        file_pointer: location of csv file to load
        storage_options: dictionary that contains abstract filesystem credentials
        **kwargs: arguments to pass to pandas `read_csv` loading method
    Returns:
        pandas dataframe loaded from CSV
    """
    
    return pd.read_csv(file_pointer, storage_options=storage_options, **kwargs)


def load_parquet_to_pandas(file_pointer: FilePointer, storage_options: dict = {}, **kwargs) -> pd.DataFrame:
    """Load a parquet file to a pandas dataframe

    Args:
        file_pointer: location of parquet file to load
        storage_options: dictionary that contains abstract filesystem credentials
        **kwargs: arguments to pass to pandas `read_parquet` loading method
    Returns:
        pandas dataframe loaded from parquet
    """
    return pd.read_parquet(file_pointer, storage_options=storage_options, **kwargs)


def write_dataframe_to_csv(dataframe: pd.DataFrame, file_pointer: FilePointer, storage_options: dict = {}, **kwargs):
    """Write a pandas DataFrame to a CSV file

    Args:
        dataframe: DataFrame to write
        file_pointer: location of file to write to
        storage_options: dictionary that contains abstract filesystem credentials
        **kwargs: args to pass to pandas `to_csv` method
    """
    
    output = io.StringIO()
    output = dataframe.to_csv(**kwargs)
    write_string_to_file(file_pointer, output, storage_options=storage_options)


def write_dataframe_to_parquet(dataframe, file_pointer, storage_options: dict={}, **kwargs):
    """Write a pandas DataFrame to a parquet file

    Args:
        dataframe: DataFrame to write
        file_pointer: location of file to write to
        storage_options: dictionary that contains abstract filesystem credentials
        **kwargs: args to pass to pandas `to_csv` method
    """

    fs, file_pointer = get_fs(file_pointer=file_pointer, storage_options=storage_options)
    with tempfile.NamedTemporaryFile() as _tmp_file:
        with fs.open(file_pointer, "wb") as _parquet_file:
            dataframe.to_parquet(_tmp_file.name)
            _parquet_file.write(_tmp_file.read())


def read_parquet_metadata(file_pointer: FilePointer, storage_options: dict={}, **kwargs) -> pq.FileMetaData:
    """Read FileMetaData from footer of a single Parquet file.

    Args:
        file_pointer: location of file to read metadata from
        storage_options: dictionary that contains abstract filesystem credentials
        **kwargs: additional arguments to be passed to pyarrow.parquet.read_metadata
    """
    fs, file_pointer = get_fs(file_pointer=file_pointer, storage_options=storage_options)

    if fs.protocol != "file" and len(file_pointer) and file_pointer[0] == "/":
        file_pointer = file_pointer[1:]
    parquet_file = pq.read_metadata(
        file_pointer, filesystem=fs, **kwargs
    )
    return parquet_file


def read_parquet_dataset(dir_pointer: FilePointer, storage_options: dict = {}):
    """Read parquet dataset from directory pointer.

    Args:
        dir_pointer: location of file to read metadata from
        storage_options: dictionary that contains abstract filesystem credentials
    """

    ignore_prefixes = [
        "intermediate", 
        "_common_metadata", 
        "_metadata",
    ]

    fs, dir_pointer = get_fs(file_pointer=dir_pointer, storage_options=storage_options)

    #pyarrow.dataset requires the pointer not lead with a slash
    if fs.protocol != "file" and len(dir_pointer) and dir_pointer[0] == "/":
        dir_pointer = dir_pointer[1:]

    dataset = pds.dataset(
        dir_pointer,
        filesystem=fs,
        exclude_invalid_files=True,
        format="parquet",
        ignore_prefixes=ignore_prefixes,
    )
    return dataset


def read_parquet_file(file_pointer: FilePointer, storage_options: dict = {}):
    """Read parquet file from file pointer.

    Args:
        file_pointer: location of file to read metadata from
        storage_options: dictionary that contains abstract filesystem credentials
    """
    fs, file_pointer = get_fs(file_pointer, storage_options=storage_options)
    return pq.ParquetFile(file_pointer, filesystem=fs)


def write_parquet_metadata(
    schema: Any, file_pointer: FilePointer, metadata_collector: list | None = None, storage_options: dict = {}, **kwargs
):
    """Write a metadata only parquet file from a schema

    Args:
        schema: schema to be written
        file_pointer: location of file to be written to
        metadata_collector: where to collect metadata information
        storage_options: dictionary that contains abstract filesystem credentials
        **kwargs: additional arguments to be passed to pyarrow.parquet.write_metadata
    """

    fs, file_pointer = get_fs(file_pointer=file_pointer, storage_options=storage_options)

    if fs.protocol != "file" and len(file_pointer) and file_pointer[0] == "/":
        file_pointer = file_pointer[1:]
    
    pq.write_metadata(schema, file_pointer, metadata_collector=metadata_collector, filesystem=fs, **kwargs)


def read_fits_image(map_file_pointer: FilePointer, storage_options: dict = {}):
    """Read the object spatial distribution information from a healpix FITS file.

    Args:
        file_pointer: location of file to be written
        storage_options: dictionary that contains abstract filesystem credentials
    Returns:
        histogram (:obj:`np.ndarray`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
    """
    fs, map_file_pointer = get_fs(file_pointer=map_file_pointer, storage_options=storage_options)
    with tempfile.NamedTemporaryFile() as _tmp_file:
        with fs.open(map_file_pointer, "rb") as _map_file:
            map_data = _map_file.read()
            _tmp_file.write(map_data)
            map_fits_image = hp.read_map(_tmp_file.name)
    return map_fits_image


def write_fits_image(histogram: np.ndarray, map_file_pointer: FilePointer, storage_options: dict = {}):
    """Write the object spatial distribution information to a healpix FITS file.

    Args:
        histogram (:obj:`np.ndarray`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
        file_pointer: location of file to be written
        storage_options: dictionary that contains abstract filesystem credentials
    """
    fs, map_file_pointer = get_fs(file_pointer=map_file_pointer, storage_options=storage_options)
    with tempfile.NamedTemporaryFile() as _tmp_file:
        with fs.open(map_file_pointer, "wb") as _map_file:
            hp.write_map(_tmp_file.name, histogram, overwrite=True, dtype=np.int64)
            _map_file.write(_tmp_file.read())


def copy_tree_fs_to_fs(fs1_source: FilePointer, fs2_destination: FilePointer, storage_options1: dict={}, storage_options2: dict={}):
    """Recursive Copies directory from one filesystem to the other.

    Args:
        fs1_source: location of source directory to copy
        fs2_destination: location of destination directory to for fs1 to be written two
        storage_options1: dictionary that contains abstract filesystem1 credentials
        storage_options2: dictionary that contains abstract filesystem2 credentials
    """

    fs1, fp1 = get_fs(fs1_source, storage_options=storage_options1)
    fs2, fp2 = get_fs(fs2_destination, storage_options=storage_options2)
    copy_dir(fs1, fp1, fs2, fp2)


def copy_dir(fs1, fs1_pointer, fs2, fs2_pointer, chunksize=1024*1024):
    """Recursive method to copy directories and their contents.

    Args:
        fs1: fsspec.filesystem for the source directory contents
        fs1_pointer: source directory to copy content files
        fs2: fsspec.filesytem for destination directory
        fs2_pointer: destination directory for copied contents
    """
    folder_name = fs1_pointer.split("/")[-1]
    destination_folder = ospathjoin(fs2_pointer, folder_name)
    if destination_folder[-1] != "/":
        destination_folder += "/"
    if not fs2.exists(destination_folder):
        fs2.makedirs(destination_folder, exist_ok=True) 

    dir_contents = fs1.listdir(fs1_pointer)
    files = [x for x in dir_contents if x["type"] == "file"]

    for f in files:
        source_fname = f["name"]
        pure_fname = source_fname.split("/")[-1]
        destination_fname = ospathjoin(destination_folder, pure_fname)
        with fs1.open(source_fname, "rb") as source_file:
            with fs2.open(destination_fname, "wb") as destination_file:
                while True:
                    chunk = source_file.read(chunksize)
                    if not chunk:
                        break
                    destination_file.write(chunk)

    dirs = [x for x in dir_contents if x["type"] == "directory"]
    for d in dirs:
        source_dir = d["name"]
        copy_dir(fs1, source_dir, fs2, destination_folder)
