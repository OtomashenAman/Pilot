import os
from typing import Any


def write_prd_files(prd_pack: dict[str, Any], base_dir: str = "./generated") -> list[str]:
    written = []

    for file in prd_pack.get("files", []):
        rel_path = file["path"]
        content = file["content"]

        out_path = os.path.join(base_dir, rel_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        written.append(out_path)

    return written


def extract_added_file_content(diff_text: str) -> str:
    """
    Handles Codex-style 'Add File' patches like:

    *** Begin Patch
    *** Add File: path/to/file.py
    +line1
    +line2
    *** End Patch

    Returns the file content with leading '+' removed.
    """
    lines = diff_text.splitlines()
    output_lines = []

    in_patch = False
    for line in lines:
        if line.startswith("*** Begin Patch"):
            in_patch = True
            continue
        if line.startswith("*** End Patch"):
            break
        if not in_patch:
            continue

        if line.startswith("*** Add File:"):
            continue

        if line.startswith("+"):
            output_lines.append(line[1:])
        elif line.startswith("***"):
            continue

    return "\n".join(output_lines).rstrip() + "\n"


def write_codex_diffs(codex_diffs: dict[str, Any], base_dir: str = "./generated") -> list[str]:
    written = []

    for item in codex_diffs.get("diffs", []):
        rel_path = item["path"]
        diff_text = item["diff"]

        content = extract_added_file_content(diff_text)

        out_path = os.path.join(base_dir, rel_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        written.append(out_path)

    return written