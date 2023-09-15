import fsspec
import glob
import os
from typing import List, NewType

SUPPORTED_PROTOCOLS = ["file", "abfs", "s3"]

FilePointer = NewType("FilePointer", str)
"""Unified type for references to files."""


def get_file_protocol(pointer: FilePointer) -> str:
    f"""Method to parse filepointer for the filesystem protocol.
        if it doesn't follow the pattern of protocol://pathway/to/file, then it 
        assumes that it is a localfilesystem.
    
    Supported protocols: {SUPPORTED_PROTOCOLS}

    Args:
        pointer: filesystem pathway pointer
    
    Raises:
        NotImplementedError: if protocol is not supported
        NotImplementedError: if more than one protocol is in the FilePointer
    """

    if not isinstance(pointer, str):
        pointer = str(pointer)

    protocol = fsspec.utils.get_protocol(pointer)

    if protocol not in SUPPORTED_PROTOCOLS:
        raise NotImplementedError(f"{protocol} is not supported for hipscat!")
    return protocol


def get_fs(file_pointer: FilePointer, storage_options: dict = {}) -> fsspec.filesystem:
    """Create the abstract filesystem
    
    Args:
        file_pointer: filesystem pathway
        storage_options: dictionary that contains abstract filesystem credentials
    """
    protocol = get_file_protocol(file_pointer)
    file_pointer = get_file_pointer_for_fs(protocol, file_pointer)
    return fsspec.filesystem(protocol, **storage_options), file_pointer


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
        #return the entire filepath for local files
        if "file://" in file_pointer:
            fp = file_pointer.split("file://")[1]
        else:
            fp = file_pointer
    if protocol == "abfs":
        #return the path minus protocol+account name
        fp = file_pointer.split("abfs://")[1]
    if protocol == "s3":
        #just strip the protocol, and keep the bucket name
        fp = file_pointer.split("s3://")[1]

    return FilePointer(fp)


def get_full_file_pointer(incomplete_path: str, protocol_path: str) -> FilePointer:
    """Rebuilds the file_pointer with the protocol and account name if required"""
    protocol = get_file_protocol(protocol_path)
    return f"{protocol}://{incomplete_path}"
    

def get_file_pointer_from_path(path: str, include_protocol: str=None) -> FilePointer:
    """Returns a file pointer from a path string"""
    if include_protocol:
        path = get_full_file_pointer(path, include_protocol)
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


def does_file_or_directory_exist(pointer: FilePointer, storage_options: dict = {}) -> bool:
    """Checks if a file or directory exists for a given file pointer

    Args:
        pointer: File Pointer to check if file or directory exists at
        storage_options: dictionary that contains abstract filesystem credentials

    Returns:
        True if file or directory at `pointer` exists, False if not
    """
    fs, pointer = get_fs(pointer, storage_options)
    return fs.exists(pointer)


def is_regular_file(pointer: FilePointer, storage_options: dict = {}) -> bool:
    """Checks if a regular file (NOT a directory) exists for a given file pointer.

    Args:
        pointer: File Pointer to check if a regular file
        storage_options: dictionary that contains abstract filesystem credentials

    Returns:
        True if regular file at `pointer` exists, False if not or is a directory
    """
    fs, pointer = get_fs(pointer, storage_options)
    return fs.isfile(pointer)


def find_files_matching_path(pointer: FilePointer, *paths: str) -> List[FilePointer]:
    """Find files or directories matching the provided path parts.

    Args:
        paths: any number of directory names optionally followed by a file name.
            directory or file names may be replaced with `*` as a matcher.
        storage_options: dictionary that contains abstract filesystem credentials
    Returns:
        New file pointers to files found matching the path
    """
    matcher = append_paths_to_pointer(pointer, *paths)
    return [get_file_pointer_from_path(x) for x in glob.glob(matcher)]


def directory_has_contents(pointer: FilePointer) -> bool:
    """Checks if a directory already has some contents (any files or subdirectories)

    Args:
        pointer: File Pointer to check for existing contents
        storage_options: dictionary that contains abstract filesystem credentials

    Returns:
        True if there are any files or subdirectories below this directory.
    """
    return len(find_files_matching_path(pointer, "*")) > 0


def get_directory_contents(
        pointer: FilePointer, append_paths=True, storage_options: dict = {}
    ) -> List[FilePointer]:
    """Finds all files and directories in the specified directory.

    NBL This is not recursive, and will return only the first level of directory contents.

    Args:
        pointer: File Pointer in which to find contents
        storage_options: dictionary that contains abstract filesystem credentials

    Returns:
        New file pointers to files or subdirectories below this directory.
    """
    fs, pointer = get_fs(pointer, storage_options)
    contents = fs.listdir(pointer)
    contents = [x['name'] for x in contents]
    if len(contents) == 0:
        return []
    contents.sort()
    if append_paths:
        return [append_paths_to_pointer(pointer, x) for x in contents]
    return contents
