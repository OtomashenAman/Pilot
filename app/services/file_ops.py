import shutil
from pathlib import Path


def copy_tree(src: str, dst: str):
    src_path = Path(src)
    dst_path = Path(dst)

    if not src_path.exists():
        raise FileNotFoundError(f"Source path does not exist: {src}")

    for item in src_path.rglob("*"):
        rel = item.relative_to(src_path)
        target = dst_path / rel

        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)