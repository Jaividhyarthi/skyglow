from backend.osv_scan import applicable_fixed_versions


def test_js_yaml_same_major_fix():
    advisory = {"affected": [
        {"package": {"ecosystem": "npm", "name": "js-yaml"}, "ranges": [{"events": [{"introduced": "3.0.0"}, {"fixed": "3.15.2"}]}]},
        {"package": {"ecosystem": "npm", "name": "js-yaml"}, "ranges": [{"events": [{"introduced": "4.0.0"}, {"fixed": "4.3.2"}]}]},
    ]}
    assert applicable_fixed_versions(advisory, "js-yaml", "4.3.1") == ["4.3.2"]
    assert applicable_fixed_versions(advisory, "js-yaml", "3.15.1") == ["3.15.2"]
    assert applicable_fixed_versions(advisory, "other-package", "4.3.1") == []
    assert applicable_fixed_versions(advisory, "js-yaml", "latest") == []


def test_no_fix_for_already_newer_version():
    advisory = {"affected": [{"package": {"ecosystem": "npm", "name": "js-yaml"}, "ranges": [{"events": [{"fixed": "4.3.2"}]}]}]}
    assert applicable_fixed_versions(advisory, "js-yaml", "4.3.3") == []


def test_fix_regex_matches_real_osv_semver():
    advisory = {"affected": [{"package": {"ecosystem": "npm", "name": "js-yaml"}, "ranges": [{"type": "SEMVER", "events": [{"introduced": "4.0.0"}, {"fixed": "4.3.2"}]}]}]}
    assert applicable_fixed_versions(advisory, "js-yaml", "4.3.1") == ["4.3.2"]
