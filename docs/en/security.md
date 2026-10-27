# Security red lines

## Do

- Prefer **Tailscale CGNAT-only** SSH (firewall `RemoteAddress` = Tailscale CGNAT, default template `100.64.0.0/10`).
- Use a dedicated low-privilege account for agent access (`readonly` mode does not join Administrators).
- Keep private keys on the operator machine; paste **public** keys only into cloud bootstrap.
- Rotate / revoke by removing the pubkey and disabling the local account when access ends.
- Review generated PowerShell before running it as Administrator.

## Do not

- Open public TCP 22 “just for a minute”.
- Commit real Tailscale IPs, account names, or private keys to git or public issues.
- Reuse the same key across unrelated production hosts without a threat model.
- Paste `diagnose` output that reveals peer names you are not willing to share.

## Revoke checklist

1. Remove the pubkey from `authorized_keys` / `administrators_authorized_keys`.
2. Disable or delete the cloud local account if it was agent-only.
3. Remove the Host block from the operator `~/.ssh/config`.
4. Optionally remove the peer from your Tailscale tailnet ACL.
