from backend.python_dependencies import extract_pinned_requirements


def test_exact_pins():
    result = extract_pinned_requirements(
        "FastAPI==0.115.0\n"
        "uvicorn==0.30.6\n"
        "Requests==2.32.3\n"
    )
    assert result["packages"] == [
        ("fastapi", "0.115.0"),
        ("requests", "2.32.3"),
        ("uvicorn", "0.30.6"),
    ]
    assert result["skipped"] == []


def test_unpinned_and_ranges_are_skipped():
    result = extract_pinned_requirements(
        "fastapi>=0.100\n"
        "uvicorn\n"
        "requests==2.*\n"
        "httpx==0.27.0\n"
    )
    assert result["packages"] == [("httpx", "0.27.0")]
    assert len(result["skipped"]) == 3


def test_comments_and_name_normalization():
    result = extract_pinned_requirements(
        "# dependencies\n"
        "My_Package.Name==1.2.3 # pinned\n"
        "\n"
    )
    assert result["packages"] == [("my-package-name", "1.2.3")]
    assert result["detected"] == 1


def test_extras_and_direct_urls_are_not_scanned():
    result = extract_pinned_requirements(
        "uvicorn[standard]==0.30.6\n"
        "example @ https://example.com/example.whl\n"
    )
    assert result["packages"] == [("uvicorn", "0.30.6")]
    assert len(result["skipped"]) == 1


def test_invalid_version_is_rejected():
    result = extract_pinned_requirements(
        "requests==not-a-version\n"
    )
    assert result["packages"] == []
    assert len(result["skipped"]) == 1


def test_environment_markers_are_reported():
    result = extract_pinned_requirements(
        "httpx==0.27.0; python_version >= '3.10'\n"
    )
    assert result["packages"] == [("httpx", "0.27.0")]
    assert result["conditional"] == 1


def test_extras_are_reported():
    result = extract_pinned_requirements(
        "uvicorn[standard]==0.30.6\n"
    )
    assert result["packages"] == [("uvicorn", "0.30.6")]
    assert result["extras"] == 1
