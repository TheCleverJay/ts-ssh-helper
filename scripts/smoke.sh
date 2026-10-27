#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src
rm -rf src/ts_ssh_helper/__pycache__ tests/__pycache__
python3 -m ts_ssh_helper.cli --help >/dev/null
python3 -m ts_ssh_helper.cli --version | grep -q 0.1.0
python3 -m ts_ssh_helper.cli gen-config --alias demo --ip 100.64.0.42 | grep -q 'Host demo'
python3 -m ts_ssh_helper.cli checklist --access readonly | grep -q ACCESS_LEVEL
# diagnose may exit 1 when ssh is missing — still must print tool lines
set +e
python3 -m ts_ssh_helper.cli diagnose > /tmp/ts-ssh-diagnose.txt
diag_rc=$?
set -e
test "$diag_rc" -eq 0 -o "$diag_rc" -eq 1
grep -q 'tool ssh' /tmp/ts-ssh-diagnose.txt
rm -rf /tmp/ts-ssh-out-test && python3 -m ts_ssh_helper.cli write -o /tmp/ts-ssh-out-test --alias demo
test -f /tmp/ts-ssh-out-test/cloud_bootstrap.ps1
python3 tests/test_smoke.py
test -f SECURITY.md && test -f CONTRIBUTING.md && test -f CHANGELOG.md && test -f CODE_OF_CONDUCT.md && test -f .gitignore
# red lines (scan sources only; avoid matching this script's own pattern text)
if grep -REi 'BEGIN OPENSSH PRIVATE KEY|YOUR_APTOS_USDT_ADDRESS' src examples 2>/dev/null; then
  echo 'FAIL: secret leak' >&2; exit 1
fi
echo SMOKE_OK
