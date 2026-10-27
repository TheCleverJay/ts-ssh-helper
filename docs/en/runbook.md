# Runbook — Tailscale-only Windows OpenSSH

Scope: any local agent host → any cloud Windows box, via Tailscale private net + OpenSSH key auth.

Use `ts-ssh gen-config / gen-bootstrap / write` to materialize snippets from the variable table. Prefer **readonly** unless you need admin.

## 0. Variables

| Variable | Meaning | Example placeholder |
|---|---|---|
| `SSH_ALIAS` | Local ssh Host name | `cloud-ts` |
| `CLOUD_TAILSCALE_IP` | Cloud Tailscale IPv4 | `100.64.0.42` |
| `CLOUD_ACCOUNT` | Cloud Windows login | `agentssh` |
| `LOCAL_KEY_NAME` | Private key file under `~/.ssh` | `id_ed25519_cloud` |
| `ACCESS_LEVEL` | `admin` or `readonly` | `readonly` |
| `ALLOWED_CIDR` | Sources allowed to hit TCP 22 | `100.64.0.0/10` |
| `CLOUD_PROFILE_DIR` | Profile path for readonly authorized_keys | `C:\Users\agentssh` |

## 1. Admin vs readonly

| Mode | Group | Pubkey file |
|---|---|---|
| admin | Administrators | `C:\ProgramData\ssh\administrators_authorized_keys` |
| readonly | ordinary user | `%USERPROFILE%\.ssh\authorized_keys` |

Once an account is in Administrators, OpenSSH stops reading the user `authorized_keys` — migrate the key file when switching modes.

## 2. Bootstrap outline

1. Local: `ts-ssh gen-keygen` → run in PowerShell → copy `.pub`.
2. Local: `ts-ssh gen-config` → append to `~/.ssh/config`.
3. Cloud (admin PowerShell): `ts-ssh gen-bootstrap` → paste pubkey → review → run.
4. Firewall must allow TCP 22 **only** on Tailscale CGNAT — never public 22.
5. Verify: `ssh <SSH_ALIAS> "whoami"` and `ts-ssh diagnose --probe <SSH_ALIAS>`.

## 3. Daily use

```bash
ssh <SSH_ALIAS> "dir C:\workspace"
scp -i ~/.ssh/<LOCAL_KEY_NAME> ./file "<SSH_ALIAS>:C:/workspace/file"
```

Chinese / complex scripts: use PowerShell `-EncodedCommand` over SSH to avoid GBK mojibake.

## 4. Troubleshooting

| Symptom | Likely cause |
|---|---|
| Connection refused | sshd down / wrong ListenAddress |
| Permission denied (publickey) | wrong key, ACL, or profile path |
| Breaks after joining Administrators | key still in user authorized_keys |
| Wrong device | mixed Tailscale IPs — run `tailscale status` |

## 5. After reboot

Wait 1–2 minutes for Tailscale. Confirm sshd + Tailscale services are Automatic. If Tailscale IP changed, update `HostName` in ssh config (or use MagicDNS hostname if your tailnet allows).
