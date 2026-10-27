# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet.

## [0.1.0] — 2026-10-27

### Added
- Initial public release: `gen-config`, `gen-keygen`, `gen-bootstrap`, `checklist`, `diagnose`, `write`.
- Windows `scripts/tailscale_status.ps1` with `-Help`.
- `diagnose` never crashes on missing binaries; exits 1 when `ssh` is absent or `--probe` fails.
- Stdlib-only; bilingual docs; smoke tests.
