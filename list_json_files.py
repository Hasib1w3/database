import argparse
from pathlib import Path


def find_json_files(root: Path) -> list[Path]:
    return sorted(p for p in root.glob("**/*.json") if p.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description="List all JSON files under the given directory (relative paths).")
    parser.add_argument(
        "root",
        nargs="?",
        default=Path.cwd(),
        type=Path,
        help="Directory to scan (default: current working directory)",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        print(f"[ERROR] '{root}' does not exist or is not a directory.")
        return 1

    files = find_json_files(root)
    if not files:
        print("[INFO] No JSON files found.")
        return 0

    print(f"Found {len(files)} JSON file(s) under '{root}':\n")
    for file_path in files:
        print(file_path.relative_to(root))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
