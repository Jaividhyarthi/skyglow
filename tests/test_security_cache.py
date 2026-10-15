import asyncio
from backend import main


def test_security_scan_cache_reuses_success(monkeypatch):
    calls = []
    async def fake_scan(name):
        calls.append(name)
        return {"status": "completed", "packages_scanned": 1, "findings": []}
    monkeypatch.setattr(main, "scan_npm_lockfile", fake_scan)
    main._security_cache.clear()
    main._security_inflight.clear()
    async def run():
        first = await main.cached_security_scan("owner/repo")
        second = await main.cached_security_scan("owner/repo")
        assert first == second
    asyncio.run(run())
    assert calls == ["owner/repo"]


def test_security_scan_coalesces_concurrent_calls(monkeypatch):
    calls = []
    async def fake_scan(name):
        calls.append(name)
        await asyncio.sleep(0.01)
        return {"status": "completed", "packages_scanned": 1, "findings": []}
    monkeypatch.setattr(main, "scan_npm_lockfile", fake_scan)
    main._security_cache.clear()
    main._security_inflight.clear()
    async def run():
        a, b = await asyncio.gather(main.cached_security_scan("owner/repo"), main.cached_security_scan("owner/repo"))
        assert a == b
    asyncio.run(run())
    assert calls == ["owner/repo"]


def test_unavailable_result_is_not_cached(monkeypatch):
    calls = []
    async def fake_scan(name):
        calls.append(name)
        return {"status": "unavailable", "findings": []}
    monkeypatch.setattr(main, "scan_npm_lockfile", fake_scan)
    main._security_cache.clear()
    main._security_inflight.clear()
    async def run():
        await main.cached_security_scan("owner/repo")
        await main.cached_security_scan("owner/repo")
    asyncio.run(run())
    assert len(calls) == 2
