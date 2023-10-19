"""Set of convenience methods for testing file contents"""

import os
import re

import pyarrow as pa
import pytest

from hipscat.io.file_io.file_io import FilePointer, get_fs, load_text_file
from hipscat.io.file_io.file_pointer import does_file_or_directory_exist

# pylint: disable=missing-function-docstring, redefined-outer-name


@pytest.fixture
def assert_text_file_matches():
    def assert_text_file_matches(expected_lines, file_name, storage_options: dict = {}):
        """Convenience method to read a text file and compare the contents, line for line.

        When file contents get even a little bit big, it can be difficult to see
        the difference between an actual file and the expected contents without
        increased testing verbosity. This helper compares files line-by-line,
        using the provided strings or regular expressions.

        Notes:
            Because we check strings as regular expressions, you may need to escape some
            contents of `expected_lines`.

        Args:
            expected_lines(:obj:`string array`) list of strings, formatted as regular expressions.
            file_name (str): fully-specified path of the file to read
            storage_options (dict): dictionary of filesystem storage options
        """
        assert does_file_or_directory_exist(
            file_name, storage_options=storage_options
        ), f"file not found [{file_name}]"
        contents = load_text_file(file_name, storage_options=storage_options)

        assert len(expected_lines) == len(
            contents
        ), f"files not the same length ({len(contents)} vs {len(expected_lines)})"
        for i, expected in enumerate(expected_lines):
            assert re.match(expected, contents[i]), (
                f"files do not match at line {i+1} " f"(actual: [{contents[i]}] vs expected: [{expected}])"
            )

        # metadata_file.close()

    return assert_text_file_matches


@pytest.fixture
def copy_tree_fs_to_fs():
    def copy_tree_fs_to_fs(
        fs1_source: FilePointer,
        fs2_destination: FilePointer,
        storage_options1: dict = None,
        storage_options2: dict = None,
        existok=False,
        chunksize=1024 * 1024,
        verbose=False,
    ):
        """Recursive Copies directory from one filesystem to the other.

        Args:
            fs1_source: location of source directory to copy
            fs2_destination: location of destination directory to for fs1 to be written two
            storage_options1: dictionary that contains abstract filesystem1 credentials
            storage_options2: dictionary that contains abstract filesystem2 credentials
        """

        source_fs, source_fp = get_fs(fs1_source, storage_options=storage_options1)
        destination_fs, desintation_fp = get_fs(fs2_destination, storage_options=storage_options2)
        copy_dir(
            source_fs,
            source_fp,
            destination_fs,
            desintation_fp,
            chunksize=chunksize,
            existok=existok,
            verbose=verbose,
        )

    def copy_dir(
        source_fs,
        source_fp,
        destination_fs,
        desintation_fp,
        chunksize=1024 * 1024,
        existok=False,
        verbose=False,
    ):
        """Recursive method to copy directories and their contents.

        Args:
            fs1: fsspec.filesystem for the source directory contents
            fs1_pointer: source directory to copy content files
            fs2: fsspec.filesytem for destination directory
            fs2_pointer: destination directory for copied contents
        """
        destination_folder = os.path.join(desintation_fp, source_fp.split("/")[-1])
        if destination_folder[-1] != "/":
            destination_folder += "/"
        if not destination_fs.exists(destination_folder):
            destination_fs.makedirs(destination_folder, exist_ok=True)

        dir_contents = source_fs.listdir(source_fp)
        files = [x for x in source_fs.listdir(source_fp) if x["type"] == "file"]

        for _file in files:
            destination_fname = os.path.join(destination_folder, _file["name"].split("/")[-1])
            if not (destination_fs.exists(destination_fname) and existok):
                if verbose:
                    print(f"Creating destination folder: {destination_folder}")
                with source_fs.open(_file["name"], "rb") as source_file:
                    with destination_fs.open(destination_fname, "wb") as destination_file:
                        while True:
                            chunk = source_file.read(chunksize)
                            if not chunk:
                                break
                            destination_file.write(chunk)

        dirs = [x for x in dir_contents if x["type"] == "directory"]
        for _dir in dirs:
            copy_dir(source_fs, _dir["name"], destination_fs, destination_folder, chunksize=chunksize)

    return copy_tree_fs_to_fs


@pytest.fixture
def basic_catalog_parquet_metadata():
    return pa.schema(
        [
            pa.field("id", pa.int64()),
            pa.field("ra", pa.float64()),
            pa.field("dec", pa.float64()),
            pa.field("ra_error", pa.int64()),
            pa.field("dec_error", pa.int64()),
            pa.field("__index_level_0__", pa.int64()),
        ]
    )
