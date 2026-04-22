#!/usr/bin/env python3
"""Simple version bumping script.

Usage:
  ./scripts/bump_version.py [major|minor|patch]
  ./scripts/bump_version.py set X.Y.Z

This updates the top-level VERSION file.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "VERSION"


def read_version():
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    return "0.0.0"


def write_version(v: str):
    VERSION_FILE.write_text(v + "\n", encoding="utf-8")


def bump(ver: str, part: str) -> str:
    parts = ver.split(".")
    if len(parts) != 3:
        raise SystemExit("Invalid version: " + ver)
    major, minor, patch = map(int, parts)
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


def main(argv):
    if not argv:
        print(read_version())
        return
    cmd = argv[0]
    curr = read_version()
    if cmd == "set" and len(argv) == 2:
        new = argv[1]
    elif cmd in ("major", "minor", "patch"):
        new = bump(curr, cmd)
    else:
        raise SystemExit(
            "Usage: bump_version.py [major|minor|patch] | set X.Y.Z"
        )
    write_version(new)
    print(new)


if __name__ == "__main__":
    main(sys.argv[1:])
