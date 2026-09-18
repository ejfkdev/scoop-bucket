# ejfkdev/scoop-bucket

[中文文档](README.zh-CN.md)

Scoop bucket for [ejfkdev](https://github.com/ejfkdev) CLI tools — the Windows
counterpart to [ejfkdev/homebrew-tap](https://github.com/ejfkdev/homebrew-tap).

## Usage

```powershell
# Install a tool directly
scoop install ejfkdev/scoop-bucket/dj
scoop install ejfkdev/scoop-bucket/udf
scoop install ejfkdev/scoop-bucket/apix
scoop install ejfkdev/scoop-bucket/tspc
scoop install ejfkdev/scoop-bucket/vcc
scoop install ejfkdev/scoop-bucket/zaip
scoop install ejfkdev/scoop-bucket/saw
scoop install ejfkdev/scoop-bucket/dns
scoop install ejfkdev/scoop-bucket/oss
scoop install ejfkdev/scoop-bucket/jd
scoop install ejfkdev/scoop-bucket/dae
scoop install ejfkdev/scoop-bucket/ov
scoop install ejfkdev/scoop-bucket/jcdc
scoop install ejfkdev/scoop-bucket/pycdc
scoop install ejfkdev/scoop-bucket/avdroot
scoop install ejfkdev/scoop-bucket/ddc

# Or add the bucket first, then install by name
scoop bucket add ejfkdev https://github.com/ejfkdev/scoop-bucket
scoop install dj
```

## Available Manifests

| Manifest | Version | Commands | Description |
|----------|---------|----------|-------------|
| [dj](https://github.com/ejfkdev/dj) | 0.6.2 | `dj` | Dynamic JS File Extractor |
| [udf](https://github.com/ejfkdev/udf) | 0.6.1 | `udf` | Extract files from disk images, container archives, and filesystems |
| [apix](https://github.com/ejfkdev/apix) | 0.0.2 | `apix` | AI-friendly HTTP request minimization tool |
| [tspc](https://github.com/ejfkdev/typespec-rs) | 0.5.6 | `tspc` | TypeSpec compiler |
| [vcc](https://github.com/ejfkdev/vcc-cli) | 0.1.0 | `vcc` | VCC CLI tool |
| [zaip](https://github.com/ejfkdev/zaip) | 1.1.0 | `zaip-client`, `zaip-server` | WebSocket tunnel proxy |
| [saw](https://github.com/ejfkdev/ShellAnyWhere) | 0.2.0 | `saw-client`, `saw-server`, `saw-shell` | Terminal sessions that stay alive |
| [dns](https://github.com/ejfkdev/dns) | 0.3.0 | `dns` | Multi-server DNS query CLI (DoT/DoH/DoQ/HTTPDNS) |
| [oss](https://github.com/ejfkdev/oss) | 0.2.5 | `oss` | S3-compatible cross-cloud object storage CLI |
| [jd](https://github.com/ejfkdev/jd) | 1.0.0 | `jd` | JavaScript deobfuscator |
| [dae](https://github.com/ejfkdev/dae) | 0.1.2 | `dae` | Dart AOT snapshot debug-info exporter |
| [ov](https://github.com/ejfkdev/ov) | 0.1.1 | `ov` | Download URL version prober |
| [jcdc](https://github.com/ejfkdev/jcdc) | 0.1.2 | `jcdc` | Java class file decompiler |
| [pycdc](https://github.com/ejfkdev/pycdc) | 0.6.0 | `pycdc`, `pycdas` | Python bytecode decompiler and disassembler |
| [avdroot](https://github.com/ejfkdev/avdroot) | 0.1.1 | `avdroot` | Root an Android Studio emulator via Magisk-patched ramdisk |
| [ddc](https://github.com/ejfkdev/ddc) | 0.1.0 | `ddc` | DEX to Java decompiler |

## Architecture support

Every manifest that upstream publishes a Windows build for includes an `arm64`
block alongside `64bit`; Scoop installs the right one automatically. `apix`
additionally ships a `32bit` build.

`oss` and `dns` publish **64-bit Windows only** upstream, so those manifests
have no `arm64` entry. `ddc` publishes no Linux builds despite what the
Homebrew formula implies — irrelevant here, but worth noting when comparing the
two taps.

## How updates work

[`update_manifests.py`](update_manifests.py) mirrors the Homebrew tap's
`update_formula.py`: it reads each upstream latest release, and if the version
moved, rewrites the version, the per-architecture URLs and their SHA256 hashes.

```bash
python3 update_manifests.py           # update everything
python3 update_manifests.py dj udf    # update named manifests
python3 update_manifests.py --check   # report drift, change nothing (exit 1)
```

[`.github/workflows/auto-update.yml`](.github/workflows/auto-update.yml) runs
daily at 04:00 UTC (and on manual dispatch), validates the result, and merges
the change automatically. If the merge cannot be completed it leaves the pull
request open with a warning instead of failing the run.

[`validate_manifests.py`](validate_manifests.py) checks JSON validity, Scoop's
published schema, hash formatting, the presence of `checkver`/`autoupdate`, that
each autoupdate template reproduces the current URLs, and that every `bin` entry
resolves to a file the install step actually produces:

```bash
python3 validate_manifests.py
```