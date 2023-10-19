import os
from typing import List, NewType, Tuple

import fsspec

FilePointer = NewType("FilePointer", str)
"""Unified type for references to files."""


def get_file_protocol(pointer: FilePointer) -> str:
    """Method to parse filepointer for the filesystem protocol.
        if it doesn't follow the pattern of protocol://pathway/to/file, then it
        assumes that it is a localfilesystem.

    Args:
        pointer: filesystem pathway pointer
    """

    if not isinstance(pointer, str):
        pointer = str(pointer)

    protocol = fsspec.utils.get_protocol(pointer)

    return protocol


def get_fs(file_pointer: FilePointer, storage_options: dict = None) -> Tuple[fsspec.filesystem, FilePointer]:
    """Create the abstract filesystem

    Args:
        file_pointer: filesystem pathway
        storage_options: dictionary that contains abstract filesystem credentials
    Raises:
        ImportError if environment cannot import necessary libraries for
            fsspec filesystems.
    """
    if storage_options is None:
        storage_options = {}
    protocol = get_file_protocol(file_pointer)
    file_pointer = get_file_pointer_for_fs(protocol, file_pointer)

    try:
        file_system = fsspec.filesystem(protocol, **storage_options)
    except ImportError as error:
        raise ImportError from error

    return file_system, file_pointer


def get_file_pointer_for_fs(protocol: str, file_pointer: FilePointer) -> FilePointer:
    """Creates the filepathway from the file_pointer. Will strip the protocol so that
            the file_pointer can be accessed from the filesystem
        abfs filesystems DO NOT require the account_name in the pathway
        s3 filesystems DO require the account_name/container name in the pathway

    Args:
        protocol: str filesytem protocol, file, abfs, or s3
        file_pointer: filesystem pathway

    """
    if not isinstance(file_pointer, str):
        file_pointer = str(file_pointer)

    if protocol == "file":
        # return the entire filepath for local files
        if "file://" in file_pointer:
            split_pointer = file_pointer.split("file://")[1]
        else:
            split_pointer = file_pointer
    else:
        split_pointer = file_pointer.split(f"{protocol}://")[1]

    return FilePointer(split_pointer)


def get_full_file_pointer(incomplete_path: str, protocol_path: str) -> FilePointer:
    """Rebuilds the file_pointer with the protocol and account name if required"""
    protocol = get_file_protocol(protocol_path)
    return FilePointer(f"{protocol}://{incomplete_path}")


def get_file_pointer_from_path(path: str, include_protocol: str = None) -> FilePointer:
    """Returns a file pointer from a path string"""
    if include_protocol:
        path = get_full_file_pointer(path, include_protocol)
    return FilePointer(path)


def get_basename_from_filepointer(pointer: FilePointer) -> str:
    """Returns the base name of a regular file. May return empty string if the file is a directory.

    Args:
        pointer: `FilePointer` object to find a basename within

    Returns:
        string representation of the basename of a file.
    """
    return os.path.basename(pointer)


def strip_leading_slash_for_pyarrow(pointer: FilePointer, protocol: str) -> FilePointer:
    """Strips the leading slash for pyarrow read/write functions.
    This is required for their filesystem abstraction
    """
    if protocol != "file" and str(pointer).startswith("/"):
        pointer = FilePointer(str(pointer).replace("/", "", 1))
    return pointer


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


def does_file_or_directory_exist(pointer: FilePointer, storage_options: dict = None) -> bool:
    """Checks if a file or directory exists for a given file pointer

    Args:
        pointer: File Pointer to check if file or directory exists at
        storage_options: dictionary that contains abstract filesystem credentials

    Returns:
        True if file or directory at `pointer` exists, False if not
    """
    file_system, pointer = get_fs(pointer, storage_options)
    return file_system.exists(pointer)


def is_regular_file(pointer: FilePointer, storage_options: dict = None) -> bool:
    """Checks if a regular file (NOT a directory) exists for a given file pointer.

    Args:
        pointer: File Pointer to check if a regular file
        storage_options: dictionary that contains abstract filesystem credentials

    Returns:
        True if regular file at `pointer` exists, False if not or is a directory
    """
    file_system, pointer = get_fs(pointer, storage_options)
    return file_system.isfile(pointer)


def find_files_matching_path(
    pointer: FilePointer, *paths: str, storage_options: dict = None
) -> List[FilePointer]:
    """Find files or directories matching the provided path parts.

    Args:
        paths: any number of directory names optionally followed by a file name.
            directory or file names may be replaced with `*` as a matcher.
        storage_options: dictionary that contains abstract filesystem credentials
    Returns:
        New file pointers to files found matching the path
    """
    matcher = append_paths_to_pointer(pointer, *paths)
    file_system, pointer = get_fs(pointer, storage_options)
    return [get_file_pointer_from_path(x) for x in file_system.glob(matcher)]


def directory_has_contents(pointer: FilePointer, storage_options: dict = None) -> bool:
    """Checks if a directory already has some contents (any files or subdirectories)

    Args:
        pointer: File Pointer to check for existing contents
        storage_options: dictionary that contains abstract filesystem credentials

    Returns:
        True if there are any files or subdirectories below this directory.
    """
    return len(find_files_matching_path(pointer, "*", storage_options=storage_options)) > 0


def get_directory_contents(
    pointer: FilePointer, include_protocol=False, storage_options: dict = None
) -> List[FilePointer]:
    """Finds all files and directories in the specified directory.

    NBL This is not recursive, and will return only the first level of directory contents.

    Args:
        pointer: File Pointer in which to find contents
        include_protocol: boolean on whether or not to include the filesystem protocol in the
            returned directory contents
        storage_options: dictionary that contains abstract filesystem credentials

    Returns:
        New file pointers to files or subdirectories below this directory.
    """
    file_system, file_pointer = get_fs(pointer, storage_options)
    contents = file_system.listdir(file_pointer)
    contents = [FilePointer(x["name"]) for x in contents]

    if len(contents) == 0:
        return []

    contents.sort()
    if include_protocol:
        contents = [get_full_file_pointer(x, protocol_path=pointer) for x in contents]
    return contents
