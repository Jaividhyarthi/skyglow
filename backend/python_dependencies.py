"""Conservative extraction of exact PyPI versions from requirements files."""

import re

from packaging.requirements import InvalidRequirement, Requirement
from packaging.version import InvalidVersion, Version


def extract_pinned_requirements(content):
    """Extract exact pins, reporting lines that cannot be fully assessed."""
    packages = set()
    skipped = []
    conditional = 0
    extras = 0

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        # Remove pip hash annotations without interpreting the hashes.
        line = re.sub(
            r"\s+--hash(?:=|\s+)\S+",
            "",
            line,
        ).strip()

        # Remove ordinary trailing comments.
        line = re.split(r"\s+#", line, maxsplit=1)[0].strip()

        try:
            req = Requirement(line)

            specs = list(req.specifier)

            if (
                req.url is not None
                or len(specs) != 1
                or specs[0].operator != "=="
                or "*" in specs[0].version
            ):
                skipped.append(raw_line.strip())
                continue

            version = specs[0].version
            Version(version)

            name = re.sub(r"[-_.]+", "-", req.name).lower()
            packages.add((name, version))
            if req.extras:
                extras += 1

            # Environment markers cannot be resolved without a target.
            if req.marker is not None:
                conditional += 1

        except (InvalidRequirement, InvalidVersion, ValueError):
            skipped.append(raw_line.strip())

    return {
        "packages": sorted(packages),
        "skipped": skipped,
        "detected": len(packages) + len(skipped),
        "conditional": conditional,
        "extras": extras,
    }
