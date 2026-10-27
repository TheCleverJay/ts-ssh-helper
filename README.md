# ts-ssh-helper

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](./pyproject.toml)

**Runnable Tailscale + OpenSSH helper** for agent operators: generate `~/.ssh/config` Host blocks, local keygen / cloud bootstrap PowerShell snippets, a deployment checklist, and a local `diagnose` report — plus a Windows `tailscale_status.ps1` with `-Help`.

- English · [中文](./README.zh-CN.md)
- License: MIT · Python ≥ 3.10 · **zero deps**
- Proposed GitHub: [`YuanAqi/ts-ssh-helper`](https://github.com/YuanAqi/ts-ssh-helper)

## Why star this

Opening public TCP 22 for an agent host is a common footgun. This project turns a battle-tested **Tailscale CGNAT-only** pattern into a CLI you can actually run: print config, write snippets, diagnose whether `ssh`/`tailscale` are on PATH, optionally probe an alias in BatchMode. Docs explain admin vs readonly; code does the mechanical work.

## Install / run

```bash
PYTHONPATH=src python -m ts_ssh_helper.cli --help
# or
pip install -e .
ts-ssh --help
```

## One-command demos

```bash
# Print an ssh config Host block (placeholders — replace IP/account)
PYTHONPATH=src python -m ts_ssh_helper.cli gen-config \
  --alias cloud-ts --ip 100.64.0.42 --user agentssh --access readonly

# Local readiness report (never crashes if ssh/tailscale missing)
PYTHONPATH=src python -m ts_ssh_helper.cli diagnose
# exit 0 if ssh present; exit 1 if ssh missing or --probe failed

# Write snippets to a folder
PYTHONPATH=src python -m ts_ssh_helper.cli write -o ./out --alias cloud-ts --ip 100.64.0.42

# Full smoke
./scripts/smoke.sh
```

On Windows (with Tailscale installed):

```powershell
.\scripts\tailscale_status.ps1 -Help
$env:OPS_STATUS_NO_BROWSER=1; $env:OPS_STATUS_NO_PAUSE=1; .\scripts\tailscale_status.ps1
```

## Subcommands

| Cmd | Output |
|---|---|
| `gen-config` | `Host` block for `~/.ssh/config` |
| `gen-keygen` | Local PowerShell `ssh-keygen` snippet |
| `gen-bootstrap` | Cloud OpenSSH install + pubkey ACL + Tailscale-only firewall |
| `checklist` | Markdown variable table |
| `diagnose` | ssh/scp/tailscale PATH + optional `--probe ALIAS` |
| `write` | All of the above into `-o DIR` |

### Exit codes

| Code | Meaning |
|---|---|
| **0** | Success (`diagnose`: ssh client present) |
| **1** | `diagnose`: ssh missing, or `--probe` failed |
| **2** | argparse usage error |

## Limitations (honesty)

- Snippets are **templates** — review before pasting into an admin PowerShell.
- Default IP `100.64.0.1` is a placeholder, not your machine.
- `diagnose` prints whatever your local Tailscale CLI returns; do not paste that output into public issues if it contains peer names you care about.
- Does not install Tailscale or OpenSSH for you.

## Docs

- [docs/en/runbook.md](./docs/en/runbook.md) — full bootstrap & daily use
- [docs/zh/runbook.md](./docs/zh/runbook.md)
- [docs/en/security.md](./docs/en/security.md) — red lines & revoke
- [docs/zh/security.md](./docs/zh/security.md)

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) · [中文](./CONTRIBUTING.zh-CN.md).  
[SECURITY.md](./SECURITY.md) · [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) · [CHANGELOG.md](./CHANGELOG.md).

## Not included

Live Tailscale IPs, account names, private keys, passwords, paid zip packs.
