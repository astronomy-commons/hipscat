from __future__ import annotations

import json
import tempfile
import warnings
from typing import Any, Dict, Tuple, Union

import numpy as np
import pandas as pd
import pyarrow.dataset as pds
import pyarrow.parquet as pq
import yaml
from pyarrow.dataset import Dataset

import hipscat.pixel_math.healpix_shim as hp
from hipscat.io.file_io.file_pointer import FilePointer, get_fs, strip_leading_slash_for_pyarrow


def make_directory(
    file_pointer: FilePointer,
    exist_ok: bool = False,
    *,
    file_system=None,
    storage_options: Union[Dict[Any, Any], None] = None,
):
    """Make a directory at a given file pointer

    Will raise an error if a directory already exists, unless `exist_ok` is True in which case
    any existing directories will be left unmodified

    Args:
        file_pointer: location in file system to make directory
        exist_ok: Default False. If false will raise error if directory exists. If true existing
            directories will be ignored and not modified
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials

    Raises:
        OSError
    """
    file_system, file_pointer = get_fs(file_pointer, file_system=file_system, storage_options=storage_options)
    file_system.makedirs(file_pointer, exist_ok=exist_ok)


def unnest_headers_for_pandas(storage_options: Union[Dict[Any, Any], None]) -> Union[Dict[Any, Any], None]:
    """Handle storage options for pandas read/write methods.
    This is needed because fsspec http storage options are nested under the "headers" key,
    see https://github.com/astronomy-commons/hipscat/issues/295
    """
    if storage_options is not None and "headers" in storage_options:
        # Copy the storage options to avoid modifying the original dictionary
        storage_options_copy = storage_options.copy()
        headers = storage_options_copy.pop("headers")
        return {**storage_options_copy, **headers}
    return storage_options


def remove_directory(
    file_pointer: FilePointer,
    ignore_errors=False,
    *,
    file_system=None,
    storage_options: Union[Dict[Any, Any], None] = None,
):
    """Remove a directory, and all contents, recursively.

    Args:
        file_pointer: directory in file system to remove
        ignore_errors: if True errors resulting from failed removals will be ignored
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials
    """

    file_system, file_pointer = get_fs(
        file_pointer=file_pointer, file_system=file_system, storage_options=storage_options
    )
    if ignore_errors:
        try:
            file_system.rm(file_pointer, recursive=True)
        except Exception:  # pylint: disable=broad-except
            # fsspec doesn't have a "ignore_errors" field in the rm method
            pass
    else:
        file_system.rm(file_pointer, recursive=True)


def write_string_to_file(
    file_pointer: FilePointer,
    string: str,
    encoding: str = "utf-8",
    *,
    file_system=None,
    storage_options: Union[Dict[Any, Any], None] = None,
):
    """Write a string to a text file

    Args:
        file_pointer: file location to write file to
        string: string to write to file
        encoding: Default: 'utf-8', encoding method to write to file with
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials
    """
    file_system, file_pointer = get_fs(file_pointer, file_system=file_system, storage_options=storage_options)
    with file_system.open(file_pointer, "w", encoding=encoding) as _file:
        _file.write(string)


def load_text_file(
    file_pointer: FilePointer,
    encoding: str = "utf-8",
    *,
    file_system=None,
    storage_options: Union[Dict[Any, Any], None] = None,
):
    """Load a text file content to a list of strings.

    Args:
        file_pointer: location of file to read
        encoding: string encoding method used by the file
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials
    Returns:
        text contents of file.
    """
    file_system, file_pointer = get_fs(file_pointer, file_system=file_system, storage_options=storage_options)
    with file_system.open(file_pointer, "r", encoding=encoding) as _text_file:
        text_file = _text_file.readlines()

    return text_file


def load_json_file(
    file_pointer: FilePointer,
    encoding: str = "utf-8",
    *,
    file_system=None,
    storage_options: Union[Dict[Any, Any], None] = None,
) -> dict:
    """Load a json file to a dictionary

    Args:
        file_pointer: location of file to read
        encoding: string encoding method used by the file
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials
    Returns:
        dictionary of key value pairs loaded from the JSON file
    """

    json_dict = None
    file_system, file_pointer = get_fs(file_pointer, file_system=file_system, storage_options=storage_options)
    with file_system.open(file_pointer, "r", encoding=encoding) as json_file:
        json_dict = json.load(json_file)

    return json_dict


# pylint: disable=unused-argument
def load_csv_to_pandas(
    file_pointer: FilePointer,
    *,
    file_system=None,
    storage_options: Union[Dict[Any, Any], None] = None,
    **kwargs,
) -> pd.DataFrame:
    """Load a csv file to a pandas dataframe

    Args:
        file_pointer: location of csv file to load
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials
        **kwargs: arguments to pass to pandas `read_csv` loading method
    Returns:
        pandas dataframe loaded from CSV
    """
    pd_storage_option = unnest_headers_for_pandas(storage_options)
    return pd.read_csv(file_pointer, storage_options=pd_storage_option, **kwargs)


def load_parquet_to_pandas(
    file_pointer: FilePointer,
    *,
    file_system=None,
    storage_options: Union[Dict[Any, Any], None] = None,
    **kwargs,
) -> pd.DataFrame:
    """Load a parquet file to a pandas dataframe

    Args:
        file_pointer: location of parquet file to load
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials
        **kwargs: arguments to pass to pandas `read_parquet` loading method
    Returns:
        pandas dataframe loaded from parquet
    """
    pd_storage_option = unnest_headers_for_pandas(storage_options)
    return pd.read_parquet(file_pointer, filesystem=file_system, storage_options=pd_storage_option, **kwargs)


def write_dataframe_to_csv(
    dataframe: pd.DataFrame,
    file_pointer: FilePointer,
    *,
    file_system=None,
    storage_options: Union[Dict[Any, Any], None] = None,
    **kwargs,
):
    """Write a pandas DataFrame to a CSV file

    Args:
        dataframe: DataFrame to write
        file_pointer: location of file to write to
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials
        **kwargs: args to pass to pandas `to_csv` method
    """
    output = dataframe.to_csv(**kwargs)
    write_string_to_file(file_pointer, output, file_system=file_system, storage_options=storage_options)


def write_dataframe_to_parquet(
    dataframe: pd.DataFrame,
    file_pointer,
    *,
    file_system=None,
    storage_options: Union[Dict[Any, Any], None] = None,
):
    """Write a pandas DataFrame to a parquet file

    Args:
        dataframe: DataFrame to write
        file_pointer: location of file to write to
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials
    """
    dataframe.to_parquet(file_pointer, filesystem=file_system, storage_options=storage_options)


def read_parquet_metadata(
    file_pointer: FilePointer,
    *,
    file_system=None,
    storage_options: Union[Dict[Any, Any], None] = None,
    **kwargs,
) -> pq.FileMetaData:
    """Read FileMetaData from footer of a single Parquet file.

    Args:
        file_pointer: location of file to read metadata from
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials
        **kwargs: additional arguments to be passed to pyarrow.parquet.read_metadata
    """
    file_system, file_pointer = get_fs(
        file_pointer=file_pointer, file_system=file_system, storage_options=storage_options
    )

    file_pointer = strip_leading_slash_for_pyarrow(file_pointer, protocol=file_system.protocol)

    parquet_file = pq.read_metadata(file_pointer, filesystem=file_system, **kwargs)
    return parquet_file


def read_parquet_dataset(
    source: FilePointer, *, file_system=None, storage_options: Union[Dict[Any, Any], None] = None, **kwargs
) -> Tuple[FilePointer, Dataset]:
    """Read parquet dataset from directory pointer or list of files.

    Note that pyarrow.dataset reads require that directory pointers don't contain a
    leading slash, and the protocol prefix may additionally be removed. As such, we also return
    the directory path that is formatted for pyarrow ingestion for follow-up.

    See more info on source specification and possible kwargs at
    https://arrow.apache.org/docs/python/generated/pyarrow.dataset.dataset.html

    Args:
        source: directory, path, or list of paths to read data from
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials

    Returns:
        Tuple containing a path to the dataset (that is formatted for pyarrow ingestion)
        and the dataset read from disk.
    """
    # pyarrow.dataset requires the pointer not lead with a slash
    if pd.api.types.is_list_like(source) and len(source) > 0:
        sample_pointer = source[0]
        file_system, sample_pointer = get_fs(
            file_pointer=sample_pointer, file_system=file_system, storage_options=storage_options
        )
        source = [strip_leading_slash_for_pyarrow(path, file_system.protocol) for path in source]
    else:
        file_system, source = get_fs(
            file_pointer=source, file_system=file_system, storage_options=storage_options
        )
        source = strip_leading_slash_for_pyarrow(source, file_system.protocol)

    dataset = pds.dataset(
        source,
        filesystem=file_system,
        format="parquet",
        **kwargs,
    )
    return (source, dataset)


def read_parquet_file(
    file_pointer: FilePointer, *, file_system=None, storage_options: Union[Dict[Any, Any], None] = None
):
    """Read parquet file from file pointer.

    Args:
        file_pointer: location of file to read metadata from
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials
    """
    file_system, file_pointer = get_fs(file_pointer, file_system=file_system, storage_options=storage_options)
    return pq.ParquetFile(file_pointer, filesystem=file_system)


def write_parquet_metadata(
    schema: Any,
    file_pointer: FilePointer,
    metadata_collector: list | None = None,
    *,
    file_system=None,
    storage_options: Union[Dict[Any, Any], None] = None,
    **kwargs,
):
    """Write a metadata only parquet file from a schema

    Args:
        schema: schema to be written
        file_pointer: location of file to be written to
        metadata_collector: where to collect metadata information
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials
        **kwargs: additional arguments to be passed to pyarrow.parquet.write_metadata
    """

    file_system, file_pointer = get_fs(
        file_pointer=file_pointer, file_system=file_system, storage_options=storage_options
    )

    file_pointer = strip_leading_slash_for_pyarrow(file_pointer, protocol=file_system.protocol)
    pq.write_metadata(
        schema, file_pointer, metadata_collector=metadata_collector, filesystem=file_system, **kwargs
    )


def read_fits_image(
    map_file_pointer: FilePointer, *, file_system=None, storage_options: Union[Dict[Any, Any], None] = None
):
    """Read the object spatial distribution information from a healpix FITS file.

    Args:
        file_pointer: location of file to be written
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials
    Returns:
        one-dimensional numpy array of long integers where the
        value at each index corresponds to the number of objects found at the healpix pixel.
    """
    file_system, map_file_pointer = get_fs(
        file_pointer=map_file_pointer, file_system=file_system, storage_options=storage_options
    )
    with tempfile.NamedTemporaryFile() as _tmp_file:
        with file_system.open(map_file_pointer, "rb") as _map_file:
            map_data = _map_file.read()
            _tmp_file.write(map_data)
            map_fits_image = hp.read_map(_tmp_file.name, nest=True, h=True)
            header_dict = dict(map_fits_image[1])
            if header_dict["ORDERING"] != "NESTED":
                warnings.warn(
                    "point_map.fits file written in RING ordering, due to "
                    "https://github.com/astronomy-commons/hipscat/issues/271. "
                    "Converting to NESTED."
                )
                map_fits_image = hp.read_map(_tmp_file.name)
                return map_fits_image
            return map_fits_image[0]


def write_fits_image(
    histogram: np.ndarray,
    map_file_pointer: FilePointer,
    *,
    file_system=None,
    storage_options: Union[Dict[Any, Any], None] = None,
):
    """Write the object spatial distribution information to a healpix FITS file.

    Args:
        histogram (:obj:`np.ndarray`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
        file_pointer: location of file to be written
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials
    """
    file_system, map_file_pointer = get_fs(
        file_pointer=map_file_pointer, file_system=file_system, storage_options=storage_options
    )
    with tempfile.NamedTemporaryFile() as _tmp_file:
        with file_system.open(map_file_pointer, "wb") as _map_file:
            hp.write_map(_tmp_file.name, histogram, overwrite=True, dtype=np.int64, nest=True)
            _map_file.write(_tmp_file.read())


def read_yaml(
    file_handle: FilePointer, *, file_system=None, storage_options: Union[Dict[Any, Any], None] = None
):
    """Reads yaml file from filesystem.

    Args:
        file_handle: location of yaml file
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials
    """
    file_system, file_handle = get_fs(
        file_pointer=file_handle, file_system=file_system, storage_options=storage_options
    )
    with file_system.open(file_handle, "r", encoding="utf-8") as _file:
        metadata = yaml.safe_load(_file)
    return metadata


def delete_file(
    file_handle: FilePointer, *, file_system=None, storage_options: Union[Dict[Any, Any], None] = None
):
    """Deletes file from filesystem.

    Args:
        file_handle: location of file pointer
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains filesystem credentials
    """
    file_system, file_handle = get_fs(
        file_pointer=file_handle, file_system=file_system, storage_options=storage_options
    )
    file_system.rm(file_handle)


def read_parquet_file_to_pandas(
    file_pointer: FilePointer,
    *,
    file_system=None,
    storage_options: Union[Dict[Any, Any], None] = None,
    **kwargs,
) -> pd.DataFrame:
    """Reads a parquet file to a pandas DataFrame

    Args:
        file_pointer (FilePointer): File Pointer to a parquet file
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains filesystem credentials
        **kwargs: Additional arguments to pass to pandas read_parquet method

    Returns:
        Pandas DataFrame with the data from the parquet file
    """
    pd_storage_option = unnest_headers_for_pandas(storage_options)
    return pd.read_parquet(file_pointer, filesystem=file_system, storage_options=pd_storage_option, **kwargs)
