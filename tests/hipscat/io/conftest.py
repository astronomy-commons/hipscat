"""Set of convenience methods for testing file contents"""

import os
import re

import pyarrow as pa
import pytest

from hipscat.io.file_io.file_pointer import (
    does_file_or_directory_exist
)
from hipscat.io.file_io.file_io import (
    load_text_file
)
# pylint: disable=missing-function-docstring, redefined-outer-name


@pytest.fixture
def assert_text_file_matches():
    def assert_text_file_matches(expected_lines, file_name, storage_options: dict={}):
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
        assert does_file_or_directory_exist(file_name, storage_options=storage_options), f"file not found [{file_name}]"
        contents = load_text_file(file_name, storage_options=storage_options)
        #with open(file_name, "r", encoding="utf-8") as metadata_file:
        #    contents = metadata_file.readlines()

        assert len(expected_lines) == len(
            contents
        ), f"files not the same length ({len(contents)} vs {len(expected_lines)})"
        for i, expected in enumerate(expected_lines):
            assert re.match(expected, contents[i]), (
                f"files do not match at line {i+1} " f"(actual: [{contents[i]}] vs expected: [{expected}])"
            )

        #metadata_file.close()

    return assert_text_file_matches


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

@pytest.fixture
def example_abstract_file_path():
    return "abfs://treasuremap/hipscat/pytests"

@pytest.fixture
def example_abstract_file_path_storage_options():
    storage_options = {
        "account_key" : os.environ.get("ABFS_LINCCDATA_ACCOUNT_KEY"),
        "account_name" : os.environ.get("ABFS_LINCCDATA_ACCOUNT_NAME")
    }
    return storage_options