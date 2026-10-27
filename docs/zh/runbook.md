# 运维手册 — 仅 Tailscale 的 Windows OpenSSH

范围：任意本地 Agent 主机 → 任意云端 Windows，经 Tailscale 私网 + OpenSSH 密钥登录。

用 `ts-ssh gen-config / gen-bootstrap / write` 把变量表落成片段。默认 **readonly**，除非明确需要 admin。

## 0. 变量

| 变量 | 含义 | 占位示例 |
|---|---|---|
| `SSH_ALIAS` | 本地 ssh Host 名 | `cloud-ts` |
| `CLOUD_TAILSCALE_IP` | 云端 Tailscale IPv4 | `100.64.0.42` |
| `CLOUD_ACCOUNT` | 云端 Windows 账号 | `agentssh` |
| `LOCAL_KEY_NAME` | `~/.ssh` 下私钥文件名 | `id_ed25519_cloud` |
| `ACCESS_LEVEL` | `admin` 或 `readonly` | `readonly` |
| `ALLOWED_CIDR` | 允许访问 TCP 22 的来源 | `100.64.0.0/10` |
| `CLOUD_PROFILE_DIR` | readonly 的 Profile 路径 | `C:\Users\agentssh` |

## 1. Admin 与 readonly

账号一旦加入 Administrators，OpenSSH 就不再读用户目录下的 `authorized_keys`，切换模式时必须迁移公钥文件。

## 2. 初始化提纲

1. 本地：`ts-ssh gen-keygen` → PowerShell 执行 → 复制 `.pub`
2. 本地：`ts-ssh gen-config` → 追加到 `~/.ssh/config`
3. 云端（管理员 PowerShell）：`ts-ssh gen-bootstrap` → 粘贴公钥 → 审阅后执行
4. 防火墙只对 Tailscale CGNAT 放行 22 —— **绝不** 对公网开放
5. 验证：`ssh <SSH_ALIAS> "whoami"`，以及 `ts-ssh diagnose --probe <SSH_ALIAS>`

## 3. 日常

```bash
ssh <SSH_ALIAS> "dir C:\workspace"
scp -i ~/.ssh/<LOCAL_KEY_NAME> ./file "<SSH_ALIAS>:C:/workspace/file"
```

中文或复杂脚本：经 SSH 使用 PowerShell `-EncodedCommand`，避免 GBK 乱码。

## 4. 排障

| 现象 | 可能原因 |
|---|---|
| Connection refused | sshd 未起 / ListenAddress 不对 |
| Permission denied (publickey) | 公钥内容、ACL 或 Profile 路径不对 |
| 加入管理员后突然失败 | 公钥仍在用户 authorized_keys |
| 连错机器 | Tailscale IP 混用 — 跑 `tailscale status` |

## 5. 重启之后

等 Tailscale 1–2 分钟；确认 sshd 与 Tailscale 为 Automatic；若 IP 变了，更新 ssh config 的 `HostName`。
