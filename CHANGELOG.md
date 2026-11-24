# Changelog

Changes to the plan format and command output must be recorded here. FPTK is in its experimental 0.x series.

## [Unreleased] — CSV contract and JSON Schema

- Added a versioned, standalone Draft 2020-12 JSON Schema with valid and invalid fixtures.
- Added tests for structural agreement and explicit runtime-only constraints.
- Added a test-only jsonschema dependency; the runtime remains dependency-free.

- Added synthetic, tracked input/output fixtures for byte-exact UTF-8/CRLF CSV exports.
- Added CLI and library regression tests for deterministic week/set ordering, blank
  optional fields, Unicode, quoting, and four common formula-leading characters.
- Documented spreadsheet security limitations and Git line-ending preservation.
- No change to the `1.0` JSON schema or `export_csv` output format.

## [0.1.0] — initial public alpha

- Strict schema-versioned JSON plan validation, immutable data models and explicit error paths.
- Deterministic weekly and whole-plan counts of sessions, sets and repetitions.
- Python CLI (`validate`, `summary`, `export-csv`) with size limits and overwrite protection.
- Formula-neutralized CSV export with documented stable columns, UTF-8 and CRLF.
- 31 automated tests and green GitHub CI for Python 3.11, 3.12 and 3.13.
- Public quickstart, Python API guide, release notes, maintainer guidance and contribution issues.

**Limitations:** alpha API, source distribution only (no PyPI), no training safety evaluation, no demonstrated third-party adoption.