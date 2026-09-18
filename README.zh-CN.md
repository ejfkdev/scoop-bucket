# ejfkdev/scoop-bucket

[English](README.md)

[ejfkdev](https://github.com/ejfkdev) 命令行工具的 Scoop bucket，对应
[ejfkdev/homebrew-tap](https://github.com/ejfkdev/homebrew-tap) 的 Windows 版本。

## 使用方法

```powershell
# 直接安装
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

# 或者先添加 bucket，再按名称安装
scoop bucket add ejfkdev https://github.com/ejfkdev/scoop-bucket
scoop install dj
```

## 可用软件包

| 软件包 | 版本 | 命令 | 说明 |
|--------|------|------|------|
| [dj](https://github.com/ejfkdev/dj) | 0.6.2 | `dj` | 动态 JS 文件提取工具 |
| [udf](https://github.com/ejfkdev/udf) | 0.6.1 | `udf` | 从磁盘镜像、归档和文件系统中提取文件 |
| [apix](https://github.com/ejfkdev/apix) | 0.0.2 | `apix` | 面向 AI 的 HTTP 请求最小化工具 |
| [tspc](https://github.com/ejfkdev/typespec-rs) | 0.5.6 | `tspc` | TypeSpec 编译器 |
| [vcc](https://github.com/ejfkdev/vcc-cli) | 0.1.0 | `vcc` | VCC 命令行工具 |
| [zaip](https://github.com/ejfkdev/zaip) | 1.1.0 | `zaip-client`、`zaip-server` | WebSocket 隧道代理 |
| [saw](https://github.com/ejfkdev/ShellAnyWhere) | 0.2.0 | `saw-client`、`saw-server`、`saw-shell` | 持久化终端会话 |
| [dns](https://github.com/ejfkdev/dns) | 0.3.0 | `dns` | 多服务器 DNS 查询工具（DoT/DoH/DoQ/HTTPDNS） |
| [oss](https://github.com/ejfkdev/oss) | 0.2.5 | `oss` | 兼容 S3 的跨云对象存储命令行工具 |
| [jd](https://github.com/ejfkdev/jd) | 1.0.0 | `jd` | JavaScript 反混淆工具 |
| [dae](https://github.com/ejfkdev/dae) | 0.1.2 | `dae` | Dart AOT 快照调试信息导出工具 |
| [ov](https://github.com/ejfkdev/ov) | 0.1.1 | `ov` | 下载链接版本探测工具 |
| [jcdc](https://github.com/ejfkdev/jcdc) | 0.1.2 | `jcdc` | Java class 文件反编译器 |
| [pycdc](https://github.com/ejfkdev/pycdc) | 0.6.0 | `pycdc`、`pycdas` | Python 字节码反编译与反汇编工具 |
| [avdroot](https://github.com/ejfkdev/avdroot) | 0.1.1 | `avdroot` | 通过 Magisk 补丁 ramdisk 获取 Android 模拟器 root |
| [ddc](https://github.com/ejfkdev/ddc) | 0.1.0 | `ddc` | DEX 转 Java 反编译器 |

## 架构支持

上游提供 Windows 构建的软件包都会同时包含 `arm64` 与 `64bit`，Scoop 会自动
选择合适的版本。`apix` 另外提供 `32bit` 构建。

`oss` 与 `dns` 上游仅发布 **64 位 Windows** 版本，因此这两个包没有 `arm64`。

## 自动更新

[`update_manifests.py`](update_manifests.py) 与 Homebrew tap 的
`update_formula.py` 逻辑一致：读取上游最新 release，若版本有变化则重写版本号、
各架构的下载链接及其 SHA256。

```bash
python3 update_manifests.py           # 更新全部
python3 update_manifests.py dj udf    # 只更新指定包
python3 update_manifests.py --check   # 仅检查是否有新版本（有则退出码 1）
```

[`.github/workflows/auto-update.yml`](.github/workflows/auto-update.yml) 每天自动
执行、校验并合并。

[`validate_manifests.py`](validate_manifests.py) 用于校验 JSON 合法性、Scoop 官方
schema、哈希格式、`checkver`/`autoupdate` 的完整性，以及每个 `bin` 项是否对应
安装步骤真正产生的文件：

```bash
python3 validate_manifests.py
```