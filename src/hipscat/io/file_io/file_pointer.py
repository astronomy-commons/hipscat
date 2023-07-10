import glob
import os
from typing import List, NewType

FilePointer = NewType("FilePointer", str)
"""Unified type for references to files."""


def get_file_pointer_from_path(path: str) -> FilePointer:
    """Returns a file pointer from a path string"""
    return FilePointer(path)


def append_paths_to_pointer(pointer: FilePointer, *paths: str) -> FilePointer:
    """Append directories and/or a file name to a specified file pointer.

    Args:
        pointer: `FilePointer` object to add path to
        paths: any number of directory names optionally followed by a file name to append to the
            pointer

    Returns:
        New file pointer to path given by joining given pointer and path names
    """
    return FilePointer(os.path.join(pointer, *paths))


def does_file_or_directory_exist(pointer: FilePointer) -> bool:
    """Checks if a file or directory exists for a given file pointer

    Args:
        pointer: File Pointer to check if file or directory exists at

    Returns:
        True if file or directory at `pointer` exists, False if not
    """
    return os.path.exists(pointer)


def is_regular_file(pointer: FilePointer) -> bool:
    """Checks if a regular file (NOT a directory) exists for a given file pointer.

    Args:
        pointer: File Pointer to check if a regular file

    Returns:
        True if regular file at `pointer` exists, False if not or is a directory
    """
    return os.path.isfile(pointer)


def find_files_matching_path(*paths: str) -> List[FilePointer]:
    """Find files or directories matching the provided path parts.

    Args:
        paths: any number of directory names optionally followed by a file name.
            directory or file names may be replaced with `*` as a matcher.
    Returns:
        New file pointers to files found matching the path
    """
    matcher = append_paths_to_pointer(*paths)
    return [get_file_pointer_from_path(x) for x in glob.glob(matcher)]


def directory_has_contents(pointer: FilePointer) -> bool:
    """Checks if a directory already has some contents (any files or subdirectories)

    Args:
        pointer: File Pointer to check for existing contents

    Returns:
        True if there are any files or subdirectories below this directory.
    """
    return len(find_files_matching_path(pointer, "*")) > 0


def get_directory_contents(pointer: FilePointer) -> List[FilePointer]:
    """Finds all files and directories in the specified directory.

    NBL This is not recursive, and will return only the first level of directory contents.

    Args:
        pointer: File Pointer in which to find contents

    Returns:
        New file pointers to files or subdirectories below this directory.
    """
    contents = os.listdir(pointer)
    if len(contents) == 0:
        return []
    contents.sort()
    return [append_paths_to_pointer(pointer, x) for x in contents]
