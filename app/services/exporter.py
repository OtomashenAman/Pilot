import os
from typing import Any


def write_prd_files(prd_pack: dict[str, Any], base_dir: str = "/app/generated") -> list[str]:
    written: list[str] = []

    for file in prd_pack.get("files", []):
        rel_path = file["path"]
        content = file["content"]

        out_path = os.path.join(base_dir, rel_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        written.append(out_path)

    return written


def _extract_from_begin_patch(diff_text: str) -> str:
    """
    Handles style:

    *** Begin Patch
    *** Add File: path/to/file.py
    +line1
    +line2
    *** End Patch
    """
    lines = diff_text.splitlines()
    output_lines: list[str] = []
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
        if line.startswith("*** Update File:"):
            continue
        if line.startswith("*** Delete File:"):
            continue
        if line.startswith("@@"):
            continue
        if line.startswith("---"):
            continue
        if line.startswith("+++"):
            continue

        if line.startswith("+"):
            output_lines.append(line[1:])
        elif line.startswith("\\ No newline at end of file"):
            continue
        elif line.startswith("***"):
            continue
        else:
            # ignore context/removal lines for now
            continue

    return "\n".join(output_lines).rstrip() + "\n" if output_lines else ""


def _extract_from_plus_header(diff_text: str) -> str:
    """
    Handles style:

    +++ path/to/file.py
    +line1
    +line2
    """
    lines = diff_text.splitlines()
    output_lines: list[str] = []
    saw_header = False

    for line in lines:
        if line.startswith("+++ "):
            saw_header = True
            continue

        if not saw_header:
            continue

        if line.startswith("+"):
            output_lines.append(line[1:])
        elif line.startswith("\\ No newline at end of file"):
            continue
        else:
            # ignore non-added lines
            continue

    return "\n".join(output_lines).rstrip() + "\n" if output_lines else ""


def _extract_plain_content(diff_text: str) -> str:
    """
    Fallback when diff is already raw file content or not in recognized patch format.
    """
    return diff_text.rstrip() + "\n" if diff_text.strip() else ""


def extract_file_content(diff_text: str) -> str:
    diff_text = (diff_text or "").strip()
    if not diff_text:
        return ""

    if "*** Begin Patch" in diff_text:
        content = _extract_from_begin_patch(diff_text)
        if content:
            return content

    if diff_text.startswith("+++ ") or "\n+++ " in diff_text:
        content = _extract_from_plus_header(diff_text)
        if content:
            return content

    return _extract_plain_content(diff_text)


def write_codex_diffs(codex_diffs: dict[str, Any], base_dir: str = "/app/generated") -> list[str]:
    written: list[str] = []

    for item in codex_diffs.get("diffs", []):
        rel_path = item["path"]
        diff_text = item["diff"]

        content = extract_file_content(diff_text)

        out_path = os.path.join(base_dir, rel_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        written.append(out_path)

    return written