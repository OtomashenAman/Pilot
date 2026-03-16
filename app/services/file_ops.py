import os
import shutil

EXCLUDED_DIR_NAMES = {
    "node_modules",
    ".next",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".git",
}

EXCLUDED_FILE_NAMES = {
    ".coverage",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
}


def _should_skip_dir(name: str) -> bool:
    return name in EXCLUDED_DIR_NAMES


def _should_skip_file(name: str) -> bool:
    if name in EXCLUDED_FILE_NAMES:
        return True
    return any(name.endswith(suffix) for suffix in EXCLUDED_SUFFIXES)


def copy_tree(src: str, dst: str) -> None:
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if not _should_skip_dir(d)]

        rel_root = os.path.relpath(root, src)
        dst_root = dst if rel_root == "." else os.path.join(dst, rel_root)
        os.makedirs(dst_root, exist_ok=True)

        for file_name in files:
            if _should_skip_file(file_name):
                continue

            src_file = os.path.join(root, file_name)
            dst_file = os.path.join(dst_root, file_name)
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)