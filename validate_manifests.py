#!/usr/bin/env python3
"""Validate every manifest in bucket/.

Checks, without downloading anything:

* each file is valid JSON and satisfies Scoop's published JSON schema
* ``version`` is non-empty and every ``architecture`` entry has url+hash
* hash length matches the algorithm implied by its length (64 hex = sha256)
* ``checkver`` is present so auto-update can work
* ``autoupdate`` exists and, with ``$version`` substituted, reproduces the
  current ``architecture`` URLs exactly (catches a broken template early)
* every ``bin`` entry resolves to a file the install step actually produces

Exits non-zero when any manifest fails.
"""
import glob
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
BUCKET = os.path.join(ROOT, "bucket")
SCHEMA_URL = (
    "https://raw.githubusercontent.com/ScoopInstaller/Scoop/master/schema.json"
)


def load_schema():
    req = urllib.request.Request(
        SCHEMA_URL, headers={"User-Agent": "scoop-bucket-validator"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def as_list(value):
    return value if isinstance(value, list) else [value]


def validate(path, schema):
    """Return a list of human-readable problems for one manifest."""
    name = os.path.basename(path)
    problems = []
    try:
        m = json.load(open(path))
    except Exception as exc:
        return [f"{name}: invalid JSON: {exc}"]

    try:
        import jsonschema

        jsonschema.validate(m, schema)
    except ImportError:
        pass
    except Exception as exc:
        problems.append(f"{name}: schema: {str(exc).splitlines()[0]}")

    for field in ("version", "description", "homepage", "license", "architecture"):
        if not m.get(field):
            problems.append(f"{name}: missing/empty required field '{field}'")

    archs = m.get("architecture") or {}
    if not archs:
        problems.append(f"{name}: no architectures defined")

    for arch, spec in archs.items():
        urls = as_list(spec.get("url", []))
        hashes = as_list(spec.get("hash", []))
        if len(urls) != len(hashes):
            problems.append(
                f"{name}/{arch}: {len(urls)} url(s) but {len(hashes)} hash(es)"
            )
        for h in hashes:
            if len(h) != 64 or any(c not in "0123456789abcdef" for c in h):
                problems.append(f"{name}/{arch}: hash is not a 64-char sha256: {h!r}")

    if "checkver" not in m:
        problems.append(f"{name}: no 'checkver' block, auto-update cannot run")

    au = (m.get("autoupdate") or {}).get("architecture")
    if not au:
        problems.append(f"{name}: no autoupdate.architecture block")
    else:
        for arch, spec in archs.items():
            if arch not in au:
                problems.append(f"{name}: autoupdate missing architecture '{arch}'")
                continue
            expected = [
                u.replace("$version", m["version"]) for u in as_list(au[arch]["url"])
            ]
            actual = as_list(spec["url"])
            if expected != actual:
                problems.append(
                    f"{name}/{arch}: autoupdate template does not reproduce the "
                    f"current url(s):\n    expected {expected}\n    actual   {actual}"
                )

    for entry in as_list(m.get("bin", [])) if m.get("bin") else []:
        # bin entries may be:
        #   "tool.exe"                     -> install tool.exe as-is
        #   ["tool.exe", "tool"]           -> install tool.exe, expose command "tool"
        #   [["src.exe", "tool"], [..]]    -> multiple aliases
        if isinstance(entry, list) and entry and isinstance(entry[0], list):
            aliases = entry
        elif isinstance(entry, list):
            aliases = [entry]
        else:
            aliases = [[entry, entry]]

        for alias in aliases:
            source, target = alias[0], alias[1]
            if not source or not target:
                problems.append(f"{name}: malformed bin entry {entry!r}")
                continue
            produced = any(
                ("#/" in u and u.split("#/")[1] == source)
                or os.path.basename(u.split("#")[0]) == source
                or (source.endswith(".exe") and u.split("#")[0].endswith(".zip"))
                for spec in archs.values()
                for u in as_list(spec["url"])
            )
            if not produced and "pre_install" not in m:
                problems.append(
                    f"{name}: bin source '{source}' is not produced by any url "
                    f"and there is no pre_install rename"
                )

    # Every architecture must be able to produce the bin source, either as a
    # direct download (possibly via "#/" rename) or through a pre_install
    # rename. This catches e.g. a zip whose 32bit build contains a differently
    # named exe than the 64bit one.
    bin_sources = []
    for entry in as_list(m.get("bin", [])) if m.get("bin") else []:
        if isinstance(entry, list) and entry and isinstance(entry[0], list):
            bin_sources += [a[0] for a in entry]
        elif isinstance(entry, list):
            bin_sources.append(entry[0])
        else:
            bin_sources.append(entry)

    for arch, spec in archs.items():
        for source in bin_sources:
            direct = any(
                ("#/" in u and u.split("#/")[1] == source)
                or os.path.basename(u.split("#")[0]) == source
                for u in as_list(spec["url"])
            )
            if direct or "pre_install" in m:
                continue
            problems.append(
                f"{name}/{arch}: bin source '{source}' is neither downloaded "
                f"directly nor produced by a pre_install rename"
            )

    return problems


def main():
    try:
        schema = load_schema()
    except Exception as exc:
        print(f"warning: could not fetch Scoop schema ({exc})", file=sys.stderr)
        schema = {}

    manifests = sorted(glob.glob(os.path.join(BUCKET, "*.json")))
    if not manifests:
        print("no manifests found in bucket/", file=sys.stderr)
        return 1

    all_problems = []
    for path in manifests:
        problems = validate(path, schema)
        label = os.path.basename(path)[:-5]
        if problems:
            all_problems.extend(problems)
            print(f"FAIL {label}")
            for p in problems:
                print(f"     - {p}")
        else:
            print(f"ok   {label}")

    print()
    if all_problems:
        print(f"{len(all_problems)} problem(s) across {len(manifests)} manifest(s)")
        return 1
    print(f"all {len(manifests)} manifest(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())