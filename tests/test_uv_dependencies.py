import pytest

from backend.uv_dependencies import parse_uv_lock


def test_uv_lock_extracts_pypi_packages():
    content = '''
version = 1

[[package]]
name = "FastAPI"
version = "0.115.0"
source = { registry = "https://pypi.org/simple" }

[[package]]
name = "Annotated_Types"
version = "0.7.0"
source = { registry = "https://pypi.org/simple/" }

[[package]]
name = "local-project"
version = "0.1.0"
source = { editable = "." }
'''
    result = parse_uv_lock(content)

    assert result["packages"] == [
        ("annotated-types", "0.7.0"),
        ("fastapi", "0.115.0"),
    ]
    assert result["skipped"] == 1
    assert result["detected"] == 3


def test_uv_lock_rejects_invalid_versions():
    content = '''
[[package]]
name = "example"
version = "not-a-version"
source = { registry = "https://pypi.org/simple" }
'''
    result = parse_uv_lock(content)

    assert result["packages"] == []
    assert result["skipped"] == 1


def test_uv_lock_rejects_invalid_package_structure():
    with pytest.raises(ValueError):
        parse_uv_lock('package = "invalid"')
