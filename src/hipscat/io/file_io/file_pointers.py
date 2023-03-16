import os
from typing import NewType

FilePointer = NewType("FilePointer", str)


def get_file_pointer_from_path(path: str) -> FilePointer:
    """Returns a file pointer from a path string"""
    return FilePointer(path)


def append_paths_to_pointer(pointer: FilePointer, *paths: str) -> FilePointer:
    """Append directory or file names to a specified file pointer.

    Args:
        pointer: `FilePointer` object to add path to
        paths: any number of file or directory names to append to the pointer

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
