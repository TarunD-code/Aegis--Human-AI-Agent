"""
Aegis v1.0 — File Actions
==========================
Handlers for file management operations: organizing files by extension,
creating files, renaming files, and listing duplicate files.
"""

from __future__ import annotations

import hashlib
import logging
import os
import shutil
from collections import defaultdict
from pathlib import Path

from execution.actions.app_actions import ExecutionResult
from security.whitelist import is_path_blocked

logger = logging.getLogger(__name__)

# ── Extension → Folder category mapping ─────────────────────────────────

EXTENSION_CATEGORIES: dict[str, str] = {
    # Documents
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".xls": "Documents",
    ".xlsx": "Documents",
    ".ppt": "Documents",
    ".pptx": "Documents",
    ".txt": "Documents",
    ".csv": "Documents",
    ".rtf": "Documents",
    ".odt": "Documents",
    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".svg": "Images",
    ".webp": "Images",
    ".ico": "Images",
    ".tiff": "Images",
    # Videos
    ".mp4": "Videos",
    ".avi": "Videos",
    ".mkv": "Videos",
    ".mov": "Videos",
    ".wmv": "Videos",
    ".flv": "Videos",
    ".webm": "Videos",
    # Audio
    ".mp3": "Audio",
    ".wav": "Audio",
    ".flac": "Audio",
    ".aac": "Audio",
    ".ogg": "Audio",
    ".wma": "Audio",
    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
    # Code
    ".py": "Code",
    ".js": "Code",
    ".ts": "Code",
    ".html": "Code",
    ".css": "Code",
    ".java": "Code",
    ".cpp": "Code",
    ".c": "Code",
    ".h": "Code",
    ".json": "Code",
    ".xml": "Code",
    ".yaml": "Code",
    ".yml": "Code",
    # Executables / Installers
    ".exe": "Executables",
    ".msi": "Executables",
    ".bat": "Executables",
    ".cmd": "Executables",
    ".ps1": "Executables",
}


def organize_files(action) -> ActionResult:
    """
    Organize files in a directory by moving them into sub-folders
    based on their file extension category.

    Only top-level files are moved; subdirectories are untouched.
    """
    target_dir = action.target
    if not target_dir:
        return ExecutionResult(
            success=False,
            message="No target directory specified.",
            data={"action_type": "organize_files"}
        )

    if is_path_blocked(target_dir):
        return ExecutionResult(
            success=False,
            message=f"Cannot organize files in blocked path: {target_dir}",
            data={"action_type": "organize_files"}
        )

    target_path = Path(target_dir)
    if not target_path.exists() or not target_path.is_dir():
        return ExecutionResult(
            success=False,
            message=f"Directory not found: {target_dir}",
            data={"action_type": "organize_files"}
        )

    moved_count = 0
    skipped_count = 0

    try:
        for item in target_path.iterdir():
            if not item.is_file():
                continue

            ext = item.suffix.lower()
            category = EXTENSION_CATEGORIES.get(ext, "Other")
            dest_folder = target_path / category
            dest_folder.mkdir(exist_ok=True)

            dest_file = dest_folder / item.name

            # Avoid overwriting existing files
            if dest_file.exists():
                base = item.stem
                counter = 1
                while dest_file.exists():
                    dest_file = dest_folder / f"{base}_{counter}{ext}"
                    counter += 1

            shutil.move(str(item), str(dest_file))
            moved_count += 1
            logger.debug("Moved %s → %s", item.name, dest_file)

    except PermissionError as exc:
        return ExecutionResult(
            success=False,
            message=f"Permission denied: {exc}",
            data={"action_type": "organize_files"}
        )
    except OSError as exc:
        return ExecutionResult(
            success=False,
            message=f"Error organizing files: {exc}",
            data={"action_type": "organize_files"}
        )

    return ExecutionResult(
        success=True,
        message=f"Organized {moved_count} file(s) into category folders in '{target_dir}'.",
        data={"action_type": "organize_files", "moved": moved_count, "skipped": skipped_count},
    )


def create_file(action) -> ActionResult:
    """
    Create a new file at the specified path with optional content.
    Will NOT overwrite existing files.
    """
    target = action.target
    content = action.value or ""

    if not target:
        return ExecutionResult(
            success=False,
            message="No file path specified.",
            data={"action_type": "create_file"}
        )

    if is_path_blocked(target):
        return ExecutionResult(
            success=False,
            message=f"Cannot create file in blocked path: {target}",
            data={"action_type": "create_file"}
        )

    file_path = Path(target)

    if file_path.exists():
        return ExecutionResult(
            success=False,
            message=f"File already exists: {target}. Will not overwrite.",
            data={"action_type": "create_file"}
        )

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        logger.info("Created file: %s", target)

        return ExecutionResult(
            success=True,
            message=f"Created file: {target}",
            data={"action_type": "create_file", "size_bytes": len(content.encode("utf-8"))},
        )

    except OSError as exc:
        return ExecutionResult(
            success=False,
            message=f"Failed to create file: {exc}",
            data={"action_type": "create_file"}
        )


def rename_file(action) -> ActionResult:
    """
    Rename a file from its current path to a new name.
    ``action.target`` = current file path, ``action.value`` = new name.
    """
    current_path = action.target
    new_name = action.value

    if not current_path or not new_name:
        return ExecutionResult(
            success=False,
            message="Both target (current path) and value (new name) are required.",
            data={"action_type": "rename_file"}
        )

    if is_path_blocked(current_path):
        return ExecutionResult(
            success=False,
            message=f"Cannot rename file in blocked path: {current_path}",
            data={"action_type": "rename_file"}
        )

    src = Path(current_path)
    if not src.exists():
        return ExecutionResult(
            success=False,
            message=f"Source file not found: {current_path}",
            data={"action_type": "rename_file"}
        )

    dest = src.parent / new_name

    if dest.exists():
        return ExecutionResult(
            success=False,
            message=f"A file with name '{new_name}' already exists in that directory.",
            data={"action_type": "rename_file"}
        )

    try:
        src.rename(dest)
        logger.info("Renamed %s → %s", current_path, dest)

        return ExecutionResult(
            success=True,
            message=f"Renamed '{src.name}' → '{new_name}'",
            data={"action_type": "rename_file"}
        )

    except OSError as exc:
        return ExecutionResult(
            success=False,
            message=f"Failed to rename file: {exc}",
            data={"action_type": "rename_file"}
        )


def list_duplicates(action) -> ActionResult:
    """
    Scan a directory for duplicate files by comparing SHA-256 hashes.
    Returns a list of duplicate groups.
    """
    target_dir = action.target
    if not target_dir:
        return ExecutionResult(
            success=False,
            message="No target directory specified.",
            data={"action_type": "list_duplicates"}
        )

    if is_path_blocked(target_dir):
        return ExecutionResult(
            success=False,
            message=f"Cannot scan blocked path: {target_dir}",
            data={"action_type": "list_duplicates"}
        )

    target_path = Path(target_dir)
    if not target_path.exists() or not target_path.is_dir():
        return ExecutionResult(
            success=False,
            message=f"Directory not found: {target_dir}",
            data={"action_type": "list_duplicates"}
        )

    hash_map: dict[str, list[str]] = defaultdict(list)

    try:
        for item in target_path.rglob("*"):
            if not item.is_file():
                continue
            try:
                file_hash = _hash_file(item)
                hash_map[file_hash].append(str(item))
            except (PermissionError, OSError):
                continue  # Skip unreadable files

    except OSError as exc:
        return ExecutionResult(
            success=False,
            message=f"Error scanning directory: {exc}",
            data={"action_type": "list_duplicates"}
        )

    # Filter to only groups with duplicates
    duplicates = {
        h: paths for h, paths in hash_map.items() if len(paths) > 1
    }

    total_dup_files = sum(len(paths) for paths in duplicates.values())

    return ExecutionResult(
        success=True,
        message=(
            f"Found {len(duplicates)} group(s) of duplicate files "
            f"({total_dup_files} files total) in '{target_dir}'."
        ),
        data={"action_type": "list_duplicates", "duplicate_groups": duplicates},
    )


def _hash_file(path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()
