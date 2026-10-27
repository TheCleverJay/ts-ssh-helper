# ts-ssh-helper

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](./pyproject.toml)

面向 Agent 运维的 **可运行 Tailscale + OpenSSH 助手**：生成 `~/.ssh/config` Host 块、本地 keygen / 云端 bootstrap 的 PowerShell 片段、部署变量清单、本地 `diagnose` 报告；另附带带 `-Help` 的 Windows `tailscale_status.ps1`。

- [English](./README.md) · 中文
- 许可证：MIT · Python ≥ 3.10 · **无依赖**
- 拟议仓库：[`YuanAqi/ts-ssh-helper`](https://github.com/YuanAqi/ts-ssh-helper)

## 为什么值得 Star

给 Agent 主机把公网 22 打开是常见翻车点。本项目把实战验证过的 **仅 Tailscale CGNAT** 模式收成 CLI：打印配置、写出片段、检查 `ssh`/`tailscale` 是否在 PATH，可选 BatchMode 探测别名。文档讲清 admin / readonly；机械活交给代码。

## 安装 / 运行

```bash
PYTHONPATH=src python -m ts_ssh_helper.cli --help
pip install -e .
ts-ssh --help
```

## 一条命令演示

```bash
PYTHONPATH=src python -m ts_ssh_helper.cli gen-config \
  --alias cloud-ts --ip 100.64.0.42 --user agentssh --access readonly

PYTHONPATH=src python -m ts_ssh_helper.cli diagnose   # 缺 ssh 也不崩溃；缺则退出码 1
PYTHONPATH=src python -m ts_ssh_helper.cli write -o ./out --alias cloud-ts --ip 100.64.0.42
./scripts/smoke.sh
```

## 子命令

| 命令 | 输出 |
|---|---|
| `gen-config` | `~/.ssh/config` 的 Host 块 |
| `gen-keygen` | 本地 PowerShell keygen 片段 |
| `gen-bootstrap` | 云端 OpenSSH + 公钥 ACL + 仅 Tailscale 防火墙 |
| `checklist` | Markdown 变量表 |
| `diagnose` | 本地工具就绪报告（可选 `--probe`） |
| `write` | 以上全部写入 `-o DIR` |

## 局限

- 片段是**模板**，粘进管理员 PowerShell 前请审阅。
- 默认 IP `100.64.0.1` 是占位符。
- `diagnose` 会打印本机 Tailscale CLI 的输出；若含敏感对端名，勿贴到公开 Issue。

## 文档

- [docs/zh/runbook.md](./docs/zh/runbook.md)
- [docs/en/runbook.md](./docs/en/runbook.md)
- [docs/zh/security.md](./docs/zh/security.md)

## 贡献

见 [CONTRIBUTING.md](./CONTRIBUTING.md) · [中文](./CONTRIBUTING.zh-CN.md)。  
[SECURITY.md](./SECURITY.md) · [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) · [CHANGELOG.md](./CHANGELOG.md)。

## 不包含

真实 Tailscale IP、账号、私钥、密码、付费 zip。
