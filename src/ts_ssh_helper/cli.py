"""ts-ssh CLI."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .config_gen import DeployVars, checklist, cloud_bootstrap_ps1, local_keygen_ps1, ssh_config_block
from .diagnose import diagnose_with_code


def _vars_from_args(a: argparse.Namespace) -> DeployVars:
    return DeployVars(
        ssh_alias=a.alias,
        cloud_tailscale_ip=a.ip,
        cloud_account=a.user,
        local_key_name=a.key_name,
        key_comment=a.key_comment,
        access_level=a.access,
        allowed_cidr=a.cidr,
        cloud_profile_dir=a.profile_dir,
        workspace_root=a.workspace,
    )


def add_var_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--alias", default="cloud-ts", help="ssh Host alias")
    p.add_argument("--ip", default="100.64.0.1", help="Cloud Tailscale IPv4 (placeholder default)")
    p.add_argument("--user", default="agentssh", help="Cloud Windows account")
    p.add_argument("--key-name", default="id_ed25519_cloud")
    p.add_argument("--key-comment", default="agent-to-cloud")
    p.add_argument("--access", choices=["readonly", "admin"], default="readonly")
    p.add_argument("--cidr", default="100.64.0.0/10", help="Firewall RemoteAddress")
    p.add_argument("--profile-dir", default=r"C:\Users\agentssh")
    p.add_argument("--workspace", default=r"C:\workspace")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ts-ssh",
        description="Tailscale + OpenSSH helper: gen-config, bootstrap snippets, diagnose, checklist",
    )
    parser.add_argument("--version", action="version", version=f"ts-ssh {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gen-config", help="Print ~/.ssh/config Host block")
    add_var_flags(g)

    k = sub.add_parser("gen-keygen", help="Print local PowerShell keygen snippet")
    add_var_flags(k)

    b = sub.add_parser("gen-bootstrap", help="Print cloud OpenSSH+firewall bootstrap snippet")
    add_var_flags(b)

    c = sub.add_parser("checklist", help="Print markdown variable checklist")
    add_var_flags(c)

    d = sub.add_parser("diagnose", help="Local tool/Tailscale/ssh readiness report")
    d.add_argument("--probe", metavar="ALIAS", help="Optional BatchMode ssh probe to alias")

    w = sub.add_parser("write", help="Write generated files into an output directory")
    add_var_flags(w)
    w.add_argument("-o", "--out", default="./ts-ssh-out", help="Output directory")

    args = parser.parse_args(argv)

    if args.cmd == "diagnose":
        lines, code = diagnose_with_code(args.probe)
        for line in lines:
            print(line)
        return code

    v = _vars_from_args(args)
    if args.cmd == "gen-config":
        print(ssh_config_block(v), end="")
    elif args.cmd == "gen-keygen":
        print(local_keygen_ps1(v), end="")
    elif args.cmd == "gen-bootstrap":
        print(cloud_bootstrap_ps1(v), end="")
    elif args.cmd == "checklist":
        print(checklist(v), end="")
    elif args.cmd == "write":
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "ssh_config_snippet").write_text(ssh_config_block(v), encoding="utf-8")
        (out / "local_keygen.ps1").write_text(local_keygen_ps1(v), encoding="utf-8")
        (out / "cloud_bootstrap.ps1").write_text(cloud_bootstrap_ps1(v), encoding="utf-8")
        (out / "CHECKLIST.md").write_text(checklist(v), encoding="utf-8")
        print(f"wrote {out}/ssh_config_snippet, local_keygen.ps1, cloud_bootstrap.ps1, CHECKLIST.md")
    else:
        parser.error("unknown command")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
