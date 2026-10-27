"""Generate ssh config Host blocks and cloud bootstrap snippets (placeholders)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DeployVars:
    ssh_alias: str = "cloud-ts"
    cloud_tailscale_ip: str = "100.64.0.1"
    cloud_account: str = "agentssh"
    local_key_name: str = "id_ed25519_cloud"
    key_comment: str = "agent-to-cloud"
    access_level: str = "readonly"  # or admin
    allowed_cidr: str = "100.64.0.0/10"
    cloud_profile_dir: str = r"C:\Users\agentssh"
    workspace_root: str = r"C:\workspace"


def ssh_config_block(v: DeployVars) -> str:
    return f"""Host {v.ssh_alias}
    HostName {v.cloud_tailscale_ip}
    User {v.cloud_account}
    IdentityFile ~/.ssh/{v.local_key_name}
    StrictHostKeyChecking accept-new
    ConnectTimeout 10
"""


def local_keygen_ps1(v: DeployVars) -> str:
    return f"""New-Item -ItemType Directory -Path "$env:USERPROFILE\\.ssh" -Force | Out-Null
ssh-keygen -t ed25519 -C "{v.key_comment}" -f "$env:USERPROFILE\\.ssh\\{v.local_key_name}" -N '""'
Get-Content "$env:USERPROFILE\\.ssh\\{v.local_key_name}.pub"
"""


def cloud_bootstrap_ps1(v: DeployVars) -> str:
    admin_join = (
        f"Add-LocalGroupMember -Group Administrators -Member '{v.cloud_account}'\n"
        if v.access_level == "admin"
        else f"# readonly mode — do NOT join Administrators for '{v.cloud_account}'\n"
    )
    return f"""# Cloud bootstrap (admin PowerShell) — review before run. Placeholders only.
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic

# Create account if missing (set password interactively in real use)
# New-LocalUser -Name '{v.cloud_account}' -PasswordNeverExpires -Description 'Agent SSH access'
{admin_join}
$pub = '<PASTE_PUBLIC_KEY_HERE>'
if ((net localgroup administrators) -match '{v.cloud_account}') {{
  Set-Content -Path C:\\ProgramData\\ssh\\administrators_authorized_keys -Value $pub -Encoding ASCII
  icacls C:\\ProgramData\\ssh\\administrators_authorized_keys /inheritance:r /grant "SYSTEM:F" "Administrators:F"
}} else {{
  $sshdir = Join-Path '{v.cloud_profile_dir}' '.ssh'
  New-Item -ItemType Directory -Path $sshdir -Force | Out-Null
  Set-Content -Path (Join-Path $sshdir 'authorized_keys') -Value $pub -Encoding ASCII
  icacls $sshdir /inheritance:r /grant "{v.cloud_account}:(OI)(CI)F" "SYSTEM:(OI)(CI)F"
  icacls (Join-Path $sshdir 'authorized_keys') /inheritance:r /grant "{v.cloud_account}:F" "SYSTEM:F"
}}

New-NetFirewallRule -DisplayName 'OpenSSH Tailscale Only' `
  -Direction Inbound -Action Allow -Protocol TCP -LocalPort 22 `
  -RemoteAddress '{v.allowed_cidr}' -Profile Any -ErrorAction SilentlyContinue

Restart-Service sshd
Write-Host "Bootstrap template applied for access_level={v.access_level}"
"""


def checklist(v: DeployVars) -> str:
    rows = [
        ("SSH_ALIAS", v.ssh_alias),
        ("CLOUD_TAILSCALE_IP", v.cloud_tailscale_ip),
        ("CLOUD_ACCOUNT", v.cloud_account),
        ("LOCAL_KEY_NAME", v.local_key_name),
        ("KEY_COMMENT", v.key_comment),
        ("ACCESS_LEVEL", v.access_level),
        ("ALLOWED_CIDR", v.allowed_cidr),
        ("CLOUD_PROFILE_DIR", v.cloud_profile_dir),
        ("WORKSPACE_ROOT", v.workspace_root),
    ]
    lines = ["# Deployment variable checklist", ""]
    lines.append("| Variable | Value |")
    lines.append("|---|---|")
    for k, val in rows:
        lines.append(f"| `{k}` | `{val}` |")
    lines.append("")
    lines.append("Keep filled copies offline. Never commit real IPs/accounts/keys.")
    return "\n".join(lines) + "\n"
