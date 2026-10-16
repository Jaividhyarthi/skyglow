"""Extract assessable PyPI dependencies from uv.lock files."""

import tomllib

from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version


def parse_uv_lock(text: str) -> dict:
    """Parse uv.lock and return pinned PyPI packages plus coverage metadata."""
    data = tomllib.loads(text)

    records = data.get("package", [])
    if not isinstance(records, list):
        raise ValueError("Invalid uv.lock: package must be a list")

    packages = set()
    skipped = 0

    for record in records:
        if not isinstance(record, dict):
            skipped += 1
            continue

        name = record.get("name")
        version = record.get("version")
        source = record.get("source", {})

        if not isinstance(source, dict):
            skipped += 1
            continue

        registry = source.get("registry", "")
        if not isinstance(registry, str) or registry.rstrip("/") != "https://pypi.org/simple":
            skipped += 1
            continue

        if not isinstance(name, str) or not name.strip():
            skipped += 1
            continue

        if not isinstance(version, str):
            skipped += 1
            continue

        try:
            Version(version)
        except InvalidVersion:
            skipped += 1
            continue

        packages.add((canonicalize_name(name), version))

    return {
        "packages": sorted(packages),
        "skipped": skipped,
        "detected": len(records),
    }
