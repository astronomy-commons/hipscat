"""Set of convenience methods for testing file contents"""

import os
import re

import pyarrow as pa
import pytest

# pylint: disable=missing-function-docstring, redefined-outer-name


@pytest.fixture
def assert_text_file_matches():
    def assert_text_file_matches(expected_lines, file_name):
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
        """
        assert os.path.exists(file_name), f"file not found [{file_name}]"
        with open(file_name, "r", encoding="utf-8") as metadata_file:
            contents = metadata_file.readlines()

        assert len(expected_lines) == len(
            contents
        ), f"files not the same length ({len(contents)} vs {len(expected_lines)})"
        for i, expected in enumerate(expected_lines):
            assert re.match(expected, contents[i]), (
                f"files do not match at line {i+1} " f"(actual: [{contents[i]}] vs expected: [{expected}])"
            )

        metadata_file.close()

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
