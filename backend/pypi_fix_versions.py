"""Conservative extraction of PyPI fix versions from OSV advisories."""

from packaging.utils import canonicalize_name
from packaging.version import Version, InvalidVersion


def applicable_pypi_fixed_versions(advisory, package_name, installed_version):
    """Return newer PyPI fixed versions reported for the exact package.

    These are OSV fix candidates, not verified upgrade recommendations.
    """
    try:
        installed = Version(installed_version)
    except (InvalidVersion, TypeError):
        return []

    fixes = set()

    for affected in advisory.get("affected", []):
        if not isinstance(affected, dict):
            continue

        package = affected.get("package")
        if not isinstance(package, dict):
            continue

        if package.get("ecosystem") != "PyPI":
            continue

        name = package.get("name")
        if not isinstance(name, str):
            continue

        if canonicalize_name(name) != canonicalize_name(package_name):
            continue

        for rng in affected.get("ranges", []):
            if not isinstance(rng, dict):
                continue

            for event in rng.get("events", []):
                if not isinstance(event, dict):
                    continue

                fixed = event.get("fixed")
                if not isinstance(fixed, str):
                    continue

                try:
                    fixed_version = Version(fixed)
                except InvalidVersion:
                    continue

                if fixed_version > installed:
                    fixes.add(fixed)

    return sorted(fixes, key=Version)
