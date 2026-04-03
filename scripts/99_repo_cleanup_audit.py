from pathlib import Path
import csv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "results" / "reports"
OUTPUT_FILE = OUTPUT_DIR / "repo_cleanup_audit.csv"


KEEP_ALWAYS = {
    "README.md",
    "requirements.txt",
    ".gitignore",
    "LICENSE",
}

USEFUL_EXTENSIONS = {
    ".py", ".md", ".txt", ".csv", ".xlsx", ".ipynb", ".png", ".jpg", ".jpeg"
}

SUSPICIOUS_DIR_NAMES = {
    "__pycache__",
    ".ipynb_checkpoints",
    ".pytest_cache",
    ".mypy_cache",
}

TEMP_FILE_PATTERNS = [
    "~$",
    ".tmp",
    ".bak",
    ".old",
    ".orig",
]

OBSOLETE_NAME_HINTS = [
    "copy",
    "copia",
    "final_final",
    "nuevo",
    "test",
    "prueba",
    "draft",
    "borrador",
]

OLD_VS_V2_PAIRS = [
    ("unaps_clean.csv", "unaps_clean_v2.csv"),
    ("sociodemographic_clean.csv", "socio_clean_v2.csv"),
]

IMPORTANT_FOLDERS = {
    "data/raw",
    "data/processed",
    "scripts",
    "results/tables",
    "results/figures",
    "results/reports",
    "docs",
    "logs",
}


def relative_posix(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def is_in_suspicious_dir(path: Path) -> bool:
    return any(part in SUSPICIOUS_DIR_NAMES for part in path.parts)


def has_temp_pattern(name: str) -> bool:
    lower = name.lower()
    return any(pattern in lower for pattern in TEMP_FILE_PATTERNS)


def has_obsolete_hint(name: str) -> bool:
    lower = name.lower()
    return any(hint in lower for hint in OBSOLETE_NAME_HINTS)


def file_size_bytes(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return -1


def is_empty_file(path: Path) -> bool:
    return file_size_bytes(path) == 0


def notebook_is_probably_empty(path: Path) -> bool:
    if path.suffix.lower() != ".ipynb":
        return False
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return '"cells": []' in text or '"cells":[]' in text
    except OSError:
        return False


def old_file_replaced_by_v2(path: Path, all_files: set[str]) -> str | None:
    name = path.name
    for old_name, new_name in OLD_VS_V2_PAIRS:
        if name == old_name and new_name in all_files:
            return new_name
    return None


def classify_file(path: Path, all_files: set[str]) -> tuple[str, str]:
    rel = relative_posix(path)
    name = path.name
    suffix = path.suffix.lower()

    if name in KEEP_ALWAYS:
        return "keep", "core repository file"

    if is_in_suspicious_dir(path):
        return "review_delete", "cache/checkpoint directory content"

    if has_temp_pattern(name):
        return "review_delete", "temporary or lock-like file"

    replaced_by = old_file_replaced_by_v2(path, all_files)
    if replaced_by:
        return "review_delete", f"older version replaced by {replaced_by}"

    if has_obsolete_hint(name):
        return "review_delete", "filename suggests duplicate/test/draft version"

    if is_empty_file(path) and name != ".gitkeep":
        return "review_delete", "empty file"

    if notebook_is_probably_empty(path):
        return "review_delete", "empty notebook"

    if suffix not in USEFUL_EXTENSIONS and suffix != "":
        return "review", "uncommon extension; verify necessity"

    if rel.startswith("logs/") and suffix == ".log":
        return "review_delete", "runtime log; usually not needed in Git"

    if rel.startswith("results/reports/") and suffix == ".txt":
        return "keep", "useful generated report"

    if rel.startswith("results/tables/") and suffix == ".csv":
        return "keep", "useful generated analysis table"

    if rel.startswith("results/figures/") and suffix in {".png", ".jpg", ".jpeg"}:
        return "keep", "useful generated figure"

    if rel.startswith("data/raw/") and suffix in {".xlsx", ".csv"}:
        return "keep", "raw source data"

    if rel.startswith("data/processed/") and suffix == ".csv":
        return "keep", "processed dataset"

    if rel.startswith("scripts/") and suffix == ".py":
        return "keep", "pipeline script"

    if rel.startswith("docs/") and suffix in {".md", ".txt"}:
        return "keep", "documentation"

    return "keep", "no issue detected"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = [p for p in PROJECT_ROOT.rglob("*") if p.is_file()]
    all_names = {p.name for p in files}

    rows = []
    for path in sorted(files):
        rel = relative_posix(path)
        decision, reason = classify_file(path, all_names)
        rows.append({
            "path": rel,
            "size_bytes": file_size_bytes(path),
            "decision": decision,
            "reason": reason,
        })

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["path", "size_bytes", "decision", "reason"]
        )
        writer.writeheader()
        writer.writerows(rows)

    keep_n = sum(1 for r in rows if r["decision"] == "keep")
    review_n = sum(1 for r in rows if r["decision"] == "review")
    delete_n = sum(1 for r in rows if r["decision"] == "review_delete")

    print("Repository cleanup audit completed.")
    print(f"Report saved to: {OUTPUT_FILE}")
    print(f"Keep: {keep_n}")
    print(f"Review: {review_n}")
    print(f"Review/Delete: {delete_n}")


if __name__ == "__main__":
    main()