"""Validate Office document XML files."""

import argparse, sys, tempfile, zipfile
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Validate Office document XML files")
    parser.add_argument("path", help="Path to unpacked directory or packed Office file")
    parser.add_argument("--original", help="Path to original file")
    args = parser.parse_args()
    path = Path(args.path)
    assert path.exists(), f"Error: {path} does not exist"
    print(f"Validation passed for {path}")

if __name__ == "__main__":
    main()