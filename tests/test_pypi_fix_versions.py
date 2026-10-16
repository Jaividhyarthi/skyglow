from backend.pypi_fix_versions import applicable_pypi_fixed_versions as fixes


def advisory(name="example-package", events=None):
    return {
        "affected": [{
            "package": {"ecosystem": "PyPI", "name": name},
            "ranges": [{
                "type": "ECOSYSTEM",
                "events": events or [
                    {"introduced": "0"},
                    {"fixed": "2.4.1"}
                ]
            }]
        }]
    }


def test_newer_fixed_version():
    assert fixes(advisory(), "example-package", "2.4.0") == ["2.4.1"]


def test_normalized_package_names():
    assert fixes(advisory("My_Package"), "my-package", "2.0") == ["2.4.1"]


def test_other_package_not_matched():
    assert fixes(advisory(), "different-package", "2.0") == []


def test_already_fixed_version():
    assert fixes(advisory(), "example-package", "2.4.1") == []
    assert fixes(advisory(), "example-package", "2.5.0") == []


def test_invalid_versions():
    assert fixes(advisory(), "example-package", "unknown") == []
    assert fixes(advisory(events=[
        {"introduced": "0"}, {"fixed": "not-a-version"}
    ]), "example-package", "1.0") == []


def test_pep440_versions():
    data = advisory(events=[
        {"introduced": "0"},
        {"fixed": "1.0rc1"},
        {"introduced": "1.0"},
        {"fixed": "1.0.post1"}
    ])
    assert fixes(data, "example-package", "0.9") == [
        "1.0rc1", "1.0.post1"
    ]


def test_no_cross_ecosystem_fixes():
    data = advisory()
    data["affected"][0]["package"]["ecosystem"] = "npm"
    assert fixes(data, "example-package", "2.0") == []
