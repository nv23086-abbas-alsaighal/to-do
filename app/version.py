from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "VERSION"


def _load_version():
    try:
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        return "0.0.0"


__version__ = _load_version()
