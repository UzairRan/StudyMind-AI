"""
Utility functions for the backend
"""

import os
import shutil
from typing import List

def cleanup_temp_files(file_paths: List[str]):
    """
    Clean up temporary files
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up {file_path}: {e}")

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def extract_filename_from_path(file_path: str) -> str:
    """
    Extract filename from full path
    """
    return os.path.basename(file_path)

def ensure_directory(path: str):
    """
    Ensure directory exists
    """
    os.makedirs(path, exist_ok=True) 