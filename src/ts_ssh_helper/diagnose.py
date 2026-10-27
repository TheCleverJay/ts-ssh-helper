"""Local diagnostics for Tailscale + ssh client readiness (cross-platform best-effort)."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def _run(cmd: list[str], timeout: float = 8.0) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = (r.stdout or "") + (r.stderr or "")
        return r.returncode, out.strip()
    except FileNotFoundError:
        return 127, f"not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    except OSError as e:
        return 1, f"os error: {e}"


def which_tools() -> dict[str, str | None]:
    return {
        "ssh": shutil.which("ssh"),
        "scp": shutil.which("scp"),
        "ssh-keygen": shutil.which("ssh-keygen"),
        "tailscale": shutil.which("tailscale"),
    }


def read_ssh_config_hosts(config_path: Path | None = None) -> list[str]:
    path = config_path or Path.home() / ".ssh" / "config"
    if not path.is_file():
        return []
    hosts: list[str] = []
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    for line in content.splitlines():
        s = line.strip()
        if s.lower().startswith("host ") and "*" not in s:
            hosts.extend(s.split()[1:])
    return hosts


def diagnose(probe_alias: str | None = None) -> list[str]:
    """Return human-readable lines. Never raises on missing binaries."""
    lines, _code = diagnose_with_code(probe_alias)
    return lines


def diagnose_with_code(probe_alias: str | None = None) -> tuple[list[str], int]:
    """Return (lines, exit_code).

    Exit 0 when local ssh client is present (Tailscale optional).
    Exit 1 when ssh is missing or an explicit --probe failed.
    Never crashes if tools are absent.
    """
    lines: list[str] = []
    exit_code = 0
    tools = which_tools()
    for name, path in tools.items():
        lines.append(f"{'OK' if path else 'MISS'}  tool {name}: {path or 'not on PATH'}")

    if not tools.get("ssh"):
        exit_code = 1
        lines.append("HINT install OpenSSH client, then re-run diagnose")

    ts = tools.get("tailscale")
    if ts:
        code, out = _run([ts, "ip", "-4"])
        lines.append(f"{'OK' if code == 0 else 'FAIL'}  tailscale ip -4 → {out or '(empty)'}")
        code, out = _run([ts, "status"])
        preview = " | ".join(out.splitlines()[:5]) if out else "(empty)"
        lines.append(f"{'OK' if code == 0 else 'FAIL'}  tailscale status (head) → {preview}")
    else:
        lines.append("SKIP tailscale CLI missing — install from https://tailscale.com/download")

    ssh_dir = Path.home() / ".ssh"
    lines.append(f"{'OK' if ssh_dir.is_dir() else 'MISS'}  ~/.ssh directory")
    hosts = read_ssh_config_hosts()
    lines.append(f"INFO ssh config hosts: {', '.join(hosts) if hosts else '(none)'}")

    if probe_alias:
        if not tools.get("ssh"):
            lines.append("FAIL cannot probe alias — ssh missing")
            exit_code = 1
        else:
            code, out = _run(
                ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", probe_alias, "echo", "TSSSH_OK"],
                timeout=12,
            )
            ok = code == 0 and "TSSSH_OK" in out
            lines.append(f"{'OK' if ok else 'FAIL'}  ssh {probe_alias} probe → rc={code} {out[:200]}")
            if not ok:
                exit_code = 1
    return lines, exit_code
