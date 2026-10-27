"""Tests — python -m pytest tests/  OR  python tests/test_smoke.py"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = str(ROOT / "src")
sys.path.insert(0, SRC)

from ts_ssh_helper.config_gen import (
    DeployVars,
    checklist,
    cloud_bootstrap_ps1,
    local_keygen_ps1,
    ssh_config_block,
)
from ts_ssh_helper.diagnose import diagnose, diagnose_with_code, which_tools, read_ssh_config_hosts


def test_config_block():
    block = ssh_config_block(DeployVars(ssh_alias="demo", cloud_tailscale_ip="100.64.1.2"))
    assert "Host demo" in block
    assert "100.64.1.2" in block
    assert "IdentityFile" in block


def test_checklist_no_secret_markers():
    text = checklist(DeployVars())
    assert "CLOUD_TAILSCALE_IP" in text
    assert "BEGIN OPENSSH PRIVATE KEY" not in text
    assert "ACCESS_LEVEL" in text


def test_bootstrap_readonly_vs_admin():
    ro = cloud_bootstrap_ps1(DeployVars(access_level="readonly"))
    ad = cloud_bootstrap_ps1(DeployVars(access_level="admin"))
    assert "do NOT join Administrators" in ro
    assert "Add-LocalGroupMember" in ad
    assert "PASTE_PUBLIC_KEY_HERE" in ro
    assert "100.64.0.0/10" in ro


def test_keygen_snippet():
    s = local_keygen_ps1(DeployVars(local_key_name="id_ed25519_demo", key_comment="demo"))
    assert "ssh-keygen" in s
    assert "id_ed25519_demo" in s


def test_cli_help():
    env = {**os.environ, "PYTHONPATH": SRC}
    r = subprocess.run(
        [sys.executable, "-m", "ts_ssh_helper.cli", "--help"],
        capture_output=True, text=True, env=env,
    )
    assert r.returncode == 0
    for name in ("gen-config", "gen-keygen", "gen-bootstrap", "checklist", "diagnose", "write"):
        assert name in r.stdout


def test_cli_gen_config():
    env = {**os.environ, "PYTHONPATH": SRC}
    r = subprocess.run(
        [sys.executable, "-m", "ts_ssh_helper.cli", "gen-config", "--alias", "x", "--ip", "100.64.9.9"],
        capture_output=True, text=True, env=env,
    )
    assert r.returncode == 0
    assert "Host x" in r.stdout and "100.64.9.9" in r.stdout


def test_diagnose_runs_no_crash():
    lines, code = diagnose_with_code(None)
    assert isinstance(lines, list) and len(lines) >= 4
    assert any("tool ssh" in ln for ln in lines)
    assert code in (0, 1)  # 1 when ssh missing — still not a crash
    # public API still returns lines only
    assert any("tool ssh" in ln for ln in diagnose(None))


def test_which_tools_dict():
    tools = which_tools()
    assert set(tools) >= {"ssh", "scp", "ssh-keygen", "tailscale"}


def test_read_ssh_config_missing():
    assert read_ssh_config_hosts(Path("/tmp/definitely-missing-ssh-config-ts-ssh")) == []


def test_cli_write(tmp_path=None):
    env = {**os.environ, "PYTHONPATH": SRC}
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run(
            [sys.executable, "-m", "ts_ssh_helper.cli", "write", "-o", d, "--alias", "demo", "--ip", "100.64.0.42"],
            capture_output=True, text=True, env=env,
        )
        assert r.returncode == 0
        out = Path(d)
        assert (out / "ssh_config_snippet").is_file()
        assert (out / "cloud_bootstrap.ps1").is_file()
        assert (out / "CHECKLIST.md").is_file()
        assert "Host demo" in (out / "ssh_config_snippet").read_text(encoding="utf-8")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    print("all smoke tests passed")
