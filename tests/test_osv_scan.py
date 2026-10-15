from backend.osv_scan import extract_pnpm_versions


def test_pnpm_v9_scoped_and_unscoped():
    packages = {
        "react@18.2.0": {},
        "@babel/core@7.24.0": {},
        "react-dom@18.2.0(react@18.2.0)": {},
        "workspace-package@link:../pkg": {},
    }
    assert extract_pnpm_versions(packages) == {
        ("react", "18.2.0"),
        ("@babel/core", "7.24.0"),
        ("react-dom", "18.2.0"),
    }


def test_pnpm_v8_legacy_and_invalid():
    packages = {
        "/lodash@4.17.21": {},
        "/@scope/pkg@1.0.0-beta.1": {},
        "file:../local": {},
        "bad@latest": {},
    }
    assert extract_pnpm_versions(packages) == {
        ("lodash", "4.17.21"),
        ("@scope/pkg", "1.0.0-beta.1"),
    }


def test_tailwind_pnpm_v9_package_keys():
    # Representative package keys from Tailwind CSS pnpm lockfile v9.
    packages = {
        "@alloc/quick-lru@5.2.0": {"resolution": {"integrity": "sha512-test"}},
        "@emnapi/core@1.11.3": {"resolution": {"integrity": "sha512-test"}},
        "react@19.2.7": {"resolution": {"integrity": "sha512-test"}},
        "vite@8.2.0(@types/node@25.9.1)": {},
    }
    assert extract_pnpm_versions(packages) == {
        ("@alloc/quick-lru", "5.2.0"),
        ("@emnapi/core", "1.11.3"),
        ("react", "19.2.7"),
        ("vite", "8.2.0"),
    }
