"""Bounded OSV scanning of exact npm lockfile versions; not a full code scan."""
import base64
import os
import httpx
import json
import re
import yaml

MAX_PACKAGES = 100
MAX_LOCKFILE_BYTES = 1_500_000

def extract_pnpm_versions(packages):
    """Extract exact npm versions from pnpm package snapshot keys."""
    unique = set()
    for key in packages:
        if not isinstance(key, str):
            continue
        spec = key.lstrip("/").split("(", 1)[0]
        name, sep, version = spec.rpartition("@")
        if sep and name and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.+-]+)?", version):
            unique.add((name, version))
    return unique


async def scan_npm_lockfile(repo_name: str):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "Skyglow-Supply-Chain/1.0"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    async with httpx.AsyncClient(timeout=25, follow_redirects=False) as client:
        res = await client.get(f"https://api.github.com/repos/{repo_name}/contents/package-lock.json", headers=headers)
        lockfile = "package-lock.json"
        if res.status_code == 404:
            res = await client.get(f"https://api.github.com/repos/{repo_name}/contents/pnpm-lock.yaml", headers=headers)
            lockfile = "pnpm-lock.yaml"
        if res.status_code == 404:
            return {"status": "unsupported", "reason": "No root package-lock.json or pnpm-lock.yaml found. No dependency scan performed.", "packages_scanned": 0, "findings": []}
        if res.status_code != 200:
            return {"status": "unavailable", "reason": f"GitHub lockfile retrieval failed (HTTP {res.status_code}).", "packages_scanned": 0, "findings": []}
        data = res.json()
        if data.get("encoding") != "base64" or data.get("size", 0) > MAX_LOCKFILE_BYTES:
            return {"status": "unsupported", "reason": "Lockfile exceeds scan size limit or is not available inline.", "packages_scanned": 0, "findings": []}
        try:
            raw = base64.b64decode(data["content"], validate=False)
            if len(raw) > MAX_LOCKFILE_BYTES:
                raise ValueError("oversized lockfile")
            lock = yaml.safe_load(raw) if lockfile == "pnpm-lock.yaml" else json.loads(raw)
        except (ValueError, KeyError, TypeError, yaml.YAMLError):
            return {"status": "unsupported", "reason": "Could not parse dependency lockfile.", "packages_scanned": 0, "findings": []}
        packages = lock.get("packages") if isinstance(lock, dict) else None
        if not isinstance(packages, dict):
            return {"status": "unsupported", "reason": "Unsupported lockfile package format.", "packages_scanned": 0, "findings": []}
        unique = {}
        if lockfile == "pnpm-lock.yaml":
            unique = {entry: None for entry in extract_pnpm_versions(packages)}
        else:
            for path, meta in packages.items():
                if not path or not isinstance(meta, dict) or "node_modules/" not in path:
                    continue
                name = path.rsplit("node_modules/", 1)[-1]
                version = meta.get("version")
                if not isinstance(version, str) or not name or not version or meta.get("link"):
                    continue
                unique[(name, version)] = None
        entries = sorted(unique)
        truncated = len(entries) > MAX_PACKAGES
        entries = entries[:MAX_PACKAGES]
        if not entries:
            return {"status": "unsupported", "reason": "No versioned npm dependencies found.", "packages_scanned": 0, "findings": []}
        payload = {"queries": [{"package": {"ecosystem": "npm", "name": name}, "version": version} for name, version in entries]}
        try:
            osv = await client.post("https://api.osv.dev/v1/querybatch", json=payload, timeout=35)
            osv.raise_for_status()
            results = osv.json()["results"]
            if len(results) != len(entries):
                raise ValueError("OSV returned incomplete batch")
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            return {"status": "unavailable", "reason": "OSV lookup failed; no security conclusion can be drawn.", "packages_scanned": 0, "findings": []}
    findings = []
    for (name, version), result in zip(entries, results):
        for vuln in result.get("vulns", []):
            vid = vuln.get("id")
            if isinstance(vid, str) and vid:
                findings.append({"package": name, "version": version, "id": vid, "url": "https://osv.dev/vulnerability/" + vid})
    return {"status": "partial" if truncated else "completed", "reason": ("Only the first 100 sorted unique npm package/version pairs were scanned." if truncated else "Root "+lockfile+" dependency versions queried against OSV; not a full code or transitive reachability audit."), "packages_scanned": len(entries), "total_packages": len(unique), "findings": findings[:250], "findings_truncated": len(findings) > 250, "source": "OSV.dev querybatch", "lockfile": lockfile}
