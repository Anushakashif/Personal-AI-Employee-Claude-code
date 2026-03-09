"""
File System Tool for AI Employee Vault

Provides file operations for reading and writing company files:
- read_file(path) - Read file contents
- write_file(path, content) - Write/create files
- list_files(directory) - List directory contents

Uses Python standard library only. No external dependencies.

Usage:
    from tools.file_tool import read_file, write_file, list_files
    
    # Read a file
    content = read_file("Company_Handbook.md")
    
    # Write a file
    write_file("notes.txt", "Meeting notes here")
    
    # List files
    files = list_files(".")
"""

import os
from pathlib import Path

# Base directory for relative paths (project root)
BASE_DIR = Path(__file__).parent.parent


def read_file(path: str, encoding: str = "utf-8") -> str:
    """
    Read contents of a file.
    
    Resolves relative paths from the project root directory.
    
    Args:
        path: File path (absolute or relative to project root)
        encoding: File encoding (default: utf-8)
    
    Returns:
        File contents as string
    
    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If read permission is denied
        UnicodeDecodeError: If encoding doesn't match file
    
    Example:
        >>> content = read_file("Company_Handbook.md")
        >>> print(content[:100])
        '# Company Handbook...'
    """
    file_path = _resolve_path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if not file_path.is_file():
        raise IsADirectoryError(f"Path is a directory, not a file: {path}")
    
    return file_path.read_text(encoding=encoding)


def write_file(path: str, content: str, encoding: str = "utf-8", create_dirs: bool = True) -> bool:
    """
    Write content to a file.
    
    Creates parent directories if they don't exist (when create_dirs=True).
    Overwrites existing files.
    
    Args:
        path: File path (absolute or relative to project root)
        content: Text content to write
        encoding: File encoding (default: utf-8)
        create_dirs: If True, create parent directories automatically
    
    Returns:
        True if write successful
    
    Raises:
        PermissionError: If write permission is denied
        IsADirectoryError: If path is an existing directory
    
    Example:
        >>> write_file("reports/daily.md", "# Daily Report\\n\\nContent here")
        True
    """
    file_path = _resolve_path(path)
    
    if file_path.exists() and file_path.is_dir():
        raise IsADirectoryError(f"Cannot write to directory: {path}")
    
    if create_dirs:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_path.write_text(content, encoding=encoding)
    return True


def list_files(directory: str = ".", recursive: bool = False) -> list:
    """
    List files and directories.
    
    Args:
        directory: Directory path (default: project root)
                   Use "." for project root, or specify a subdirectory
        recursive: If True, list all files recursively
    
    Returns:
        List of file/directory names (strings)
        Returns empty list if directory doesn't exist
    
    Raises:
        NotADirectoryError: If path is not a directory
    
    Example:
        >>> list_files(".")
        ['Company_Handbook.md', 'tools', 'README.md', ...]
        
        >>> list_files("tools", recursive=True)
        ['tools/gmail_tool.py', 'tools/file_tool.py', ...]
    """
    dir_path = _resolve_path(directory)
    
    if not dir_path.exists():
        return []
    
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")
    
    if recursive:
        return sorted([str(p.relative_to(dir_path)) for p in dir_path.rglob("*")])
    
    return sorted([p.name for p in dir_path.iterdir()])


def file_exists(path: str) -> bool:
    """
    Check if a file or directory exists.
    
    Args:
        path: File or directory path
    
    Returns:
        True if exists, False otherwise
    
    Example:
        >>> file_exists("Company_Handbook.md")
        True
        >>> file_exists("nonexistent.txt")
        False
    """
    file_path = _resolve_path(path)
    return file_path.exists()


def delete_file(path: str) -> bool:
    """
    Delete a file.
    
    Args:
        path: File path to delete
    
    Returns:
        True if deleted successfully, False if file doesn't exist
    
    Raises:
        IsADirectoryError: If path is a directory (use delete_directory instead)
    
    Example:
        >>> delete_file("temp.txt")
        True
    """
    file_path = _resolve_path(path)
    
    if not file_path.exists():
        return False
    
    if file_path.is_dir():
        raise IsADirectoryError(f"Path is a directory: {path}. Use delete_directory().")
    
    file_path.unlink()
    return True


def delete_directory(path: str, recursive: bool = False) -> bool:
    """
    Delete a directory.
    
    Args:
        path: Directory path to delete
        recursive: If True, delete directory and all contents
    
    Returns:
        True if deleted successfully, False if directory doesn't exist
    
    Raises:
        NotADirectoryError: If path is not a directory
        OSError: If directory is not empty and recursive=False
    
    Example:
        >>> delete_directory("old_reports", recursive=True)
        True
    """
    dir_path = _resolve_path(path)
    
    if not dir_path.exists():
        return False
    
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")
    
    if recursive:
        import shutil
        shutil.rmtree(str(dir_path))
    else:
        dir_path.rmdir()
    
    return True


def get_file_info(path: str) -> dict:
    """
    Get file metadata.
    
    Args:
        path: File or directory path
    
    Returns:
        Dictionary with file information:
        - name: File/directory name
        - path: Full path
        - size: Size in bytes (files only)
        - is_file: True if file
        - is_dir: True if directory
        - exists: True if exists
    
    Raises:
        FileNotFoundError: If path doesn't exist
    
    Example:
        >>> info = get_file_info("Company_Handbook.md")
        >>> info["size"]
        12345
    """
    file_path = _resolve_path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    stat = file_path.stat()
    
    return {
        "name": file_path.name,
        "path": str(file_path),
        "size": stat.st_size if file_path.is_file() else 0,
        "is_file": file_path.is_file(),
        "is_dir": file_path.is_dir(),
        "exists": True
    }


def _resolve_path(path: str) -> Path:
    """
    Resolve path relative to project root.
    
    Args:
        path: File path (absolute or relative)
    
    Returns:
        Absolute Path object
    """
    file_path = Path(path)
    
    if file_path.is_absolute():
        return file_path
    
    return BASE_DIR / file_path
