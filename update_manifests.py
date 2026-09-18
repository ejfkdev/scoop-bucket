#!/usr/bin/env python3
"""Regenerate Scoop manifests from GitHub release info.

Mirrors the behaviour of ejfkdev/homebrew-tap's update_formula.py: for each
manifest, read the upstream latest release, and if the version moved, rewrite
the version, the per-architecture URLs and their sha256 hashes.

Usage:
    python3 update_manifests.py            # update every manifest
    python3 update_manifests.py dj udf     # update only the named manifests
    python3 update_manifests.py --check    # report drift, change nothing
"""
import json
import os
import subprocess
import sys
import hashlib
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
BUCKET = os.path.join(ROOT, "bucket")

# asset name template per manifest: {version} is substituted.
# None means "no binary published for this architecture".
ASSETS = {
    "dj": {
        "64bit": "dj-windows-amd64.exe#/dj.exe",
        "arm64": "dj-windows-arm64.exe#/dj.exe",
    },
    "udf": {
        "64bit": "udf_v{version}_windows_amd64.zip",
        "arm64": "udf_v{version}_windows_arm64.zip",
    },
    "apix": {
        "64bit": "apix-windows-amd64.zip",
        "32bit": "apix-windows-386.zip",
    },
    "tspc": {
        "64bit": "tspc-x86_64-pc-windows-msvc.exe#/tspc.exe",
        "arm64": "tspc-aarch64-pc-windows-msvc.exe#/tspc.exe",
    },
    "vcc": {
        "64bit": "vcc-x86_64-windows.exe",
    },
    "zaip": {
        "64bit": [
            "zaip-client_windows_amd64.exe#/zaip-client.exe",
            "zaip-server_windows_amd64.exe#/zaip-server.exe",
        ],
        "arm64": [
            "zaip-client_windows_arm64.exe#/zaip-client.exe",
            "zaip-server_windows_arm64.exe#/zaip-server.exe",
        ],
    },
    "saw": {
        "64bit": [
            "saw-client-windows-x86_64.exe#/saw-client.exe",
            "saw-server-windows-x86_64.exe#/saw-server.exe",
            "saw-shell-windows-x86_64.exe#/saw-shell.exe",
        ],
        "arm64": [
            "saw-client-windows-arm64.exe#/saw-client.exe",
            "saw-server-windows-arm64.exe#/saw-server.exe",
            "saw-shell-windows-arm64.exe#/saw-shell.exe",
        ],
    },
    "dns": {
        "64bit": "dns-{version}-x86_64-pc-windows-msvc.exe#/dns.exe",
    },
    "oss": {
        "64bit": "oss-v{version}-windows-amd64.zip",
    },
    "jd": {
        "64bit": "jd-v{version}-windows-amd64.exe#/jd.exe",
        "arm64": "jd-v{version}-windows-arm64.exe#/jd.exe",
    },
    "dae": {
        "64bit": "dae-Windows-x64.exe#/dae.exe",
        "arm64": "dae-Windows-arm64.exe#/dae.exe",
    },
    "ov": {
        "64bit": "ov-windows-amd64.exe#/ov.exe",
        "arm64": "ov-windows-arm64.exe#/ov.exe",
    },
    "jcdc": {
        "64bit": "jcdc-v{version}-windows-amd64.exe#/jcdc.exe",
        "arm64": "jcdc-v{version}-windows-arm64.exe#/jcdc.exe",
    },
    "pycdc": {
        "64bit": [
            "pycdc-x86_64-windows.exe#/pycdc.exe",
            "pycdas-x86_64-windows.exe#/pycdas.exe",
        ],
        "arm64": [
            "pycdc-aarch64-windows.exe#/pycdc.exe",
            "pycdas-aarch64-windows.exe#/pycdas.exe",
        ],
    },
    "avdroot": {
        "64bit": "avdroot_windows_amd64.exe#/avdroot.exe",
        "arm64": "avdroot_windows_arm64.exe#/avdroot.exe",
    },
    "ddc": {
        "64bit": "ddc-v{version}-windows-amd64.exe#/ddc.exe",
        "arm64": "ddc-v{version}-windows-arm64.exe#/ddc.exe",
    },
}

# Manifests whose bin name contains the version and is renamed in pre_install
# instead of via a "#/" alias.
PRE_INSTALL_RENAME = {"oss"}


def github_latest(repo):
    """Return (tag, version) for the upstream latest release."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(url, headers={"User-Agent": "scoop-bucket-updater"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    tag = data["tag_name"]
    return tag, tag.lstrip("v")


def sha256_of(url):
    req = urllib.request.Request(url, headers={"User-Agent": "scoop-bucket-updater"})
    h = hashlib.sha256()
    with urllib.request.urlopen(req, timeout=300) as r:
        for chunk in iter(lambda: r.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rewrite(manifest_path, name, version, repo):
    with open(manifest_path) as f:
        m = json.load(f)

    if m["version"] == version:
        return False

    print(f"  updating {name}: {m['version']} -> {version}")
    m["version"] = version

    base = f"https://github.com/{repo}/releases/download/v{version}"
    for arch, patterns in ASSETS[name].items():
        if isinstance(patterns, str):
            patterns = [patterns]
        urls, hashes = [], []
        for pat in patterns:
            asset = pat.format(version=version)
            dl = asset.split("#")[0]
            url = f"{base}/{dl}"
            if "#/" in asset:
                url_rw = f"{url}#/{asset.split('#/')[1]}"
            else:
                url_rw = url
            urls.append(url_rw)
            hashes.append(sha256_of(url))
            print(f"    {arch}: {dl}")
        m["architecture"][arch]["url"] = urls[0] if len(urls) == 1 else urls
        m["architecture"][arch]["hash"] = hashes[0] if len(hashes) == 1 else hashes

    with open(manifest_path, "w") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return True


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check_only = "--check" in sys.argv

    names = sorted(ASSETS) if args else sorted(
        f[:-5] for f in os.listdir(BUCKET) if f.endswith(".json")
    )

    changed = 0
    for name in names:
        path = os.path.join(BUCKET, f"{name}.json")
        if not os.path.exists(path):
            print(f"  {name}: no manifest, skipping")
            continue
        m = json.load(open(path))
        repo = m["checkver"]["github"].replace("https://github.com/", "")
        tag, version = github_latest(repo)
        if m["version"] == version:
            print(f"  {name}: up to date ({version})")
            continue
        if check_only:
            print(f"  {name}: STALE - manifest={m['version']} upstream={version}")
            changed += 1
            continue
        if rewrite(path, name, version, repo):
            changed += 1

    print(f"\n{'stale' if check_only else 'updated'}: {changed}")
    if check_only and changed:
        sys.exit(1)


if __name__ == "__main__":
    main()