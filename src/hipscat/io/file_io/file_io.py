import json
import os

import pandas as pd

from hipscat.io.file_io.file_pointers import FilePointer


def make_directory(file_pointer: FilePointer, exist_ok: bool = False):
    """Make a directory at a given file pointer

    Will raise an error if a directory already exists, unless `exist_ok` is True in which case
    any existing directories will be left unmodified

    Args:
        file_pointer: location in file system to make directory
        exist_ok: Default False. If false will raise error if directory exists. If true existing
        directories will be ignored and not modified

    Raises:
        OSError
    """
    os.makedirs(file_pointer, exist_ok=exist_ok)


def write_string_to_file(
    file_pointer: FilePointer, string: str, encoding: str = "utf-8"
):
    """Write a string to a text file

    Args:
        file_pointer: file location to write file to
        string: string to write to file
        encoding: Default: 'utf-8', encoding method to write to file with
    """
    with open(file_pointer, "w", encoding=encoding) as file:
        file.write(string + "\n")


def load_json_file(file_pointer: FilePointer, encoding: str = "utf-8") -> dict:
    """Load a json file to a dictionary

    Args:
        file_pointer: location of file to read
        encoding: string encoding method used by the file

    """
    json_dict = None
    with open(file_pointer, "r", encoding=encoding) as json_file:
        json_dict = json.load(json_file)
    return json_dict


def load_csv_to_pandas(file_pointer: FilePointer, **kwargs):
    """Load a csv file to a pandas dataframe

    Args:
        file_pointer: location of csv file to load
        **kwargs: arguments to pass to pandas `read_csv` loading method
    """
    return pd.read_csv(file_pointer, **kwargs)


def write_dataframe_to_csv(
    dataframe: pd.DataFrame, file_pointer: FilePointer, **kwargs
):
    """Write a pandas DataFrame to a CSV file

    Args:
        dataframe: DataFrame to write
        file_pointer: location of file to write to
        **kwargs: args to pass to pandas `to_csv` method
    """
    dataframe.to_csv(file_pointer, **kwargs)
