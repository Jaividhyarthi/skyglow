from backend.pypi_fix_versions import pypi_upgrade_guidance as guide


def test_smallest_newer_candidate():
    result = guide("1.26.0", ["2.2.0", "1.30.0"])
    assert result["preferred_candidate"] == "1.30.0"
    assert result["major_version_change"] is False
    assert result["candidate_count"] == 2


def test_major_version_upgrade():
    result = guide("1.26.0", ["2.2.0"])
    assert result["preferred_candidate"] == "2.2.0"
    assert result["major_version_change"] is True


def test_no_newer_candidate():
    assert guide("2.0.0", ["1.9.0", "2.0.0"]) is None
    assert guide("2.0.0", []) is None


def test_invalid_versions():
    assert guide("unknown", ["2.0.0"]) is None
    assert guide("1.0.0", ["invalid"]) is None


def test_duplicate_candidates():
    result = guide("1.0.0", ["1.2.0", "1.2.0", "2.0.0"])
    assert result["candidate_count"] == 2


def test_pep440_ordering():
    result = guide("1.0rc1", ["1.0.post1", "1.0"])
    assert result["preferred_candidate"] == "1.0"


def test_disclaimer():
    result = guide("1.0.0", ["1.1.0"])
    assert "not verified" in result["disclaimer"]
