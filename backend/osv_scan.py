"""Bounded OSV scanning of exact npm lockfile versions; not a full code scan."""
import base64
import os
import httpx
import json
import re
import yaml

MAX_PACKAGES = 600
BATCH_SIZE = 100
MAX_ADVISORY_DETAILS = 10
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
        results = []
        scanned_entries = []
        batch_failed = False
        for offset in range(0, len(entries), BATCH_SIZE):
            batch = entries[offset:offset + BATCH_SIZE]
            payload = {"queries": [{"package": {"ecosystem": "npm", "name": name}, "version": version} for name, version in batch]}
            try:
                osv = await client.post("https://api.osv.dev/v1/querybatch", json=payload, timeout=35)
                osv.raise_for_status()
                batch_results = osv.json()["results"]
                if not isinstance(batch_results, list) or len(batch_results) != len(batch):
                    raise ValueError("OSV returned incomplete batch")
            except (httpx.HTTPError, ValueError, KeyError, TypeError):
                batch_failed = True
                break
            scanned_entries.extend(batch)
            results.extend(batch_results)
        if not scanned_entries:
            return {"status": "unavailable", "reason": "OSV lookup failed before any dependency was assessed.", "packages_scanned": 0, "total_packages": len(unique), "lockfile": lockfile, "findings": []}
    findings = []
    for (name, version), result in zip(scanned_entries, results):
        for vuln in result.get("vulns", []):
            vid = vuln.get("id")
            if isinstance(vid, str) and vid:
                findings.append({"package": name, "version": version, "id": vid, "url": "https://osv.dev/vulnerability/" + vid})
    # OSV querybatch returns advisory IDs, not full severity records.
    # Enrich a bounded subset; missing data must never be interpreted as low risk.
    detail_ids = sorted({item["id"] for item in findings})[:MAX_ADVISORY_DETAILS]
    details = {}
    async with httpx.AsyncClient(timeout=12) as detail_client:
        for vid in detail_ids:
            try:
                response = await detail_client.get("https://api.osv.dev/v1/vulns/" + vid)
                response.raise_for_status()
                advisory = response.json()
                if not isinstance(advisory, dict):
                    continue
                severity = advisory.get("severity")
                scores = [x for x in severity if isinstance(x, dict) and isinstance(x.get("score"), str)] if isinstance(severity, list) else []
                details[vid] = {"summary": str(advisory.get("summary") or "")[:350],
                                "severity_scores": [{"type": str(x.get("type") or "")[:40], "score": x["score"][:180]} for x in scores[:3]],
                                "severity_label": (advisory.get("database_specific") or {}).get("severity") if isinstance(advisory.get("database_specific"), dict) and (advisory.get("database_specific") or {}).get("severity") in ("LOW", "MODERATE", "MEDIUM", "HIGH", "CRITICAL") else None,
                                "aliases": [v for v in advisory.get("aliases", []) if isinstance(v, str) and v.startswith("CVE-")][:5] if isinstance(advisory.get("aliases"), list) else [],
                                "fixed_versions": sorted({event["fixed"] for affected in advisory.get("affected", []) if isinstance(affected, dict) and (affected.get("package") or {}).get("ecosystem") == "npm" for rng in affected.get("ranges", []) if isinstance(rng, dict) for event in rng.get("events", []) if isinstance(event, dict) and isinstance(event.get("fixed"), str)})[:10] if isinstance(advisory.get("affected"), list) else []}
            except (httpx.HTTPError, ValueError, TypeError):
                continue
    for item in findings:
        item["details"] = details.get(item["id"])
    partial = truncated or batch_failed
    scanned_count = len(scanned_entries)
    remaining = len(unique) - scanned_count
    reason = (f"{scanned_count} of {len(unique)} unique dependency versions queried against OSV; "
              + (f"{remaining} unqueried due to a batch failure." if batch_failed else
                 f"{remaining} unqueried due to the {MAX_PACKAGES}-package limit." if truncated else
                 "All detected versions queried; not a full code or reachability audit."))
    return {"status": "partial" if partial else "completed",
            "reason": reason, "packages_scanned": scanned_count,
            "total_packages": len(unique), "findings": findings[:250],
            "findings_truncated": len(findings) > 250,
            "source": "OSV.dev querybatch", "lockfile": lockfile, "advisories_enriched": len(details), "advisory_detail_limit": MAX_ADVISORY_DETAILS}
