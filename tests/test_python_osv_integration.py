import asyncio
import base64
import json

import httpx

from backend.osv_scan import scan_npm_lockfile


def test_python_requirements_queries_pypi(monkeypatch):
    asyncio.run(_python_requirements_queries_pypi(monkeypatch))

async def _python_requirements_queries_pypi(monkeypatch):
    calls = []

    requirements = (
        "fastapi==0.115.0\n"
        "requests==2.32.3\n"
    )

    async def fake_get(self, url, **kwargs):
        calls.append(("GET", url))

        if url.endswith(("package-lock.json", "pnpm-lock.yaml")):
            return httpx.Response(404, request=httpx.Request("GET", url))

        if url.endswith("requirements.txt"):
            data = {
                "encoding": "base64",
                "size": len(requirements),
                "content": base64.b64encode(
                    requirements.encode()
                ).decode(),
            }
            return httpx.Response(
                200,
                json=data,
                request=httpx.Request("GET", url),
            )

        raise AssertionError(f"Unexpected GET: {url}")

    async def fake_post(self, url, **kwargs):
        assert url == "https://api.osv.dev/v1/querybatch"

        queries = kwargs["json"]["queries"]
        assert len(queries) == 2
        assert all(
            q["package"]["ecosystem"] == "PyPI"
            for q in queries
        )

        return httpx.Response(
            200,
            json={"results": [{}, {}]},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    result = await scan_npm_lockfile("example/python-project")

    assert result["status"] == "partial"
    assert result["ecosystem"] == "PyPI"
    assert "transitive dependency coverage" in result["reason"]
    assert result["packages_scanned"] == 2
    assert result["total_packages"] == 2
    assert result["findings"] == []


def test_unpinned_python_dependencies_are_partial(monkeypatch):
    asyncio.run(_unpinned_python_dependencies_are_partial(monkeypatch))

async def _unpinned_python_dependencies_are_partial(monkeypatch):
    requirements = (
        "fastapi==0.115.0\n"
        "requests>=2.0\n"
        "uvicorn\n"
    )

    async def fake_get(self, url, **kwargs):
        if url.endswith(("package-lock.json", "pnpm-lock.yaml")):
            return httpx.Response(404, request=httpx.Request("GET", url))

        if url.endswith("requirements.txt"):
            return httpx.Response(
                200,
                json={
                    "encoding": "base64",
                    "size": len(requirements),
                    "content": base64.b64encode(
                        requirements.encode()
                    ).decode(),
                },
                request=httpx.Request("GET", url),
            )

        raise AssertionError(url)

    async def fake_post(self, url, **kwargs):
        assert len(kwargs["json"]["queries"]) == 1
        return httpx.Response(
            200,
            json={"results": [{}]},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    result = await scan_npm_lockfile("example/python-project")

    assert result["status"] == "partial"
    assert result["packages_scanned"] == 1
    assert result["total_packages"] == 3
    assert result["skipped_requirements"] == 2
    assert "not assessed" in result["reason"]


def test_all_unpinned_requirements_do_not_query_osv(monkeypatch):
    asyncio.run(_all_unpinned_requirements_do_not_query_osv(monkeypatch))


async def _all_unpinned_requirements_do_not_query_osv(monkeypatch):
    requirements = "fastapi>=0.100\nuvicorn\nrequests~=2.0\n"

    async def fake_get(self, url, **kwargs):
        if url.endswith(("package-lock.json", "pnpm-lock.yaml")):
            return httpx.Response(
                404, request=httpx.Request("GET", url)
            )

        if url.endswith("requirements.txt"):
            return httpx.Response(
                200,
                json={
                    "encoding": "base64",
                    "size": len(requirements.encode()),
                    "content": base64.b64encode(
                        requirements.encode()
                    ).decode(),
                },
                request=httpx.Request("GET", url),
            )

        raise AssertionError(f"Unexpected GET: {url}")

    async def fake_post(self, url, **kwargs):
        raise AssertionError("OSV must not be queried without exact pins")

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    result = await scan_npm_lockfile("example/unpinned-python")

    assert result["status"] == "unsupported"
    assert result["ecosystem"] == "PyPI"
    assert result["packages_scanned"] == 0
    assert result["total_packages"] == 3
    assert result["skipped_requirements"] == 3
    assert result["findings"] == []


def test_uv_lock_integration(monkeypatch):
    asyncio.run(_test_uv_lock_integration(monkeypatch))


async def _test_uv_lock_integration(monkeypatch):
    lock = '''
version = 1

[[package]]
name = "FastAPI"
version = "0.115.0"
source = { registry = "https://pypi.org/simple" }

[[package]]
name = "local-project"
version = "0.1.0"
source = { editable = "." }
'''
    queries_seen = []

    async def fake_get(self, url, **kwargs):
        if url.endswith(("package-lock.json", "pnpm-lock.yaml", "requirements.txt")):
            return httpx.Response(404, request=httpx.Request("GET", url))

        if url.endswith("uv.lock"):
            return httpx.Response(
                200,
                json={
                    "encoding": "base64",
                    "size": len(lock.encode()),
                    "content": base64.b64encode(lock.encode()).decode(),
                },
                request=httpx.Request("GET", url),
            )

        raise AssertionError(f"Unexpected GET: {url}")

    async def fake_post(self, url, **kwargs):
        queries_seen.extend(kwargs["json"]["queries"])
        return httpx.Response(
            200,
            json={"results": [{"vulns": []}]},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    result = await scan_npm_lockfile("example/uv-project")

    assert result["ecosystem"] == "PyPI"
    assert result["lockfile"] == "uv.lock"
    assert result["status"] == "partial"
    assert result["packages_scanned"] == 1
    assert result["total_packages"] == 2
    assert result["skipped_requirements"] == 1
    assert queries_seen == [{
        "package": {"ecosystem": "PyPI", "name": "fastapi"},
        "version": "0.115.0",
    }]
