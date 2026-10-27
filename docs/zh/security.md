# 安全红线

## 要做

- 优先 **仅 Tailscale CGNAT** 的 SSH（防火墙 `RemoteAddress` 指向 Tailscale CGNAT，模板默认 `100.64.0.0/10`）。
- 给 Agent 用独立低权限账号（`readonly` 模式不加入 Administrators）。
- 私钥留在操作者机器；云端 bootstrap 只粘贴**公钥**。
- 访问结束后删除公钥并停用本地账号。
- 生成的 PowerShell 在管理员权限下运行前先审阅。

## 不要

- 「就开一会儿」公网 TCP 22。
- 把真实 Tailscale IP、账号、私钥提交到 git 或公开 Issue。
- 在没有威胁模型的情况下跨无关生产机复用同一把密钥。
- 粘贴含你不愿公开的对端名的 `diagnose` 输出。

## 撤销清单

1. 从 `authorized_keys` / `administrators_authorized_keys` 删除公钥。
2. 若账号专供 Agent，禁用或删除。
3. 从操作者 `~/.ssh/config` 删除 Host 块。
4. 可选：从 Tailscale ACL 移除该对端。
