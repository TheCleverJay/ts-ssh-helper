# Examples

These are **placeholders**. Replace IPs/accounts before use. Never commit real values.

```bash
# Generate a Host block with demo placeholders
PYTHONPATH=src python -m ts_ssh_helper.cli gen-config \
  --alias cloud-ts --ip 100.64.0.42 --user agentssh --access readonly

# Write all snippets into ./out
PYTHONPATH=src python -m ts_ssh_helper.cli write -o ./out \
  --alias cloud-ts --ip 100.64.0.42 --user agentssh --access readonly
```

See `docs/en/runbook.md` for the full bootstrap order.
