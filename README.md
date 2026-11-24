# Fitness Programming Toolkit (FPTK)

[![Python CI](https://github.com/splucasaugusto666/fitness-programming-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/splucasaugusto666/fitness-programming-toolkit/actions/workflows/ci.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Version:** `0.1.0` (early alpha; no stable public API guarantee). **Distribution:** GitHub source only, not PyPI.

FPTK is a small, offline Python package for **structural validation of strength-training plan data**, deterministic volume summaries, and spreadsheet-safe, set-by-set CSV exports. It is for developers, coaches and gym software integrators who want auditable data processing without a SaaS dependency.

It does **not** assess exercise safety, prescribe appropriate loads, measure outcomes, manage patients, or provide medical advice.

## Quick start

Requires **Python 3.11+**; the runtime uses only the Python standard library.

```sh
git clone https://github.com/splucasaugusto666/fitness-programming-toolkit.git
cd fitness-programming-toolkit
python -m pip install -e .
fptk validate examples/strength_program.json
fptk summary examples/strength_program.json
fptk export-csv examples/strength_program.json --output program.csv
```

The included 4-week synthetic example produces **2 sessions / 7 sets / 68 reps per week**, or **8 sessions / 28 sets / 272 reps** over four weeks. These are planned *counts*, not exercise-effectiveness or clinical assessments.

See [Getting started](docs/QUICKSTART.md) for expected output and a Python example; see [API reference](docs/API.md) and [plan format](docs/FORMAT.md) for exact rules. The CSV wire format is covered by [byte-exact regression fixtures](docs/FORMAT.md#deterministic-csv-bytes-golden-contract).

The [JSON Schema 2020-12](schemas/program-1.0.schema.json) provides a structural precheck for non-Python consumers; see [documented limits](docs/FORMAT.md#explicit-limits-of-parity). The runtime remains dependency-free.

## Typical uses

- Reject malformed workout JSON before an import to a gym or coaching app.
- Generate a deterministic review summary of a weekly program repeated for multiple weeks.
- Export a CSV with stable columns and spreadsheet-formula neutralization for untrusted text.
- Run reproducible checks in a CI pipeline, locally and without network access.

## Scope and tradeoffs

- Accepts only `schema_version: "1.0"` with explicit field and size limits; unknown keys are rejected.
- The same weekly template repeats for `weeks`. Progression, attendance, dates and individual responses are **not** modeled.
- CSV is expanded per prescribed set *per week*. This may be large within the documented input limits.
- Reads UTF-8 JSON up to 2 MB. Does not collect telemetry or require a hosted service.
- Does not claim interoperability with OpenSet, PWF or any other format; adapters require separate research and agreement on lossy fields.

## Contribute

Contributions are welcome, but **measurable utility matters more than commit counts**. Start by reproducing a bug or proposing an integration you actually need. The [JSON Schema issue #1](https://github.com/splucasaugusto666/fitness-programming-toolkit/issues/1) tracks the structural precheck. [Issue #2 (CSV fixtures)](https://github.com/splucasaugusto666/fitness-programming-toolkit/issues/2) was completed by [PR #3](https://github.com/splucasaugusto666/fitness-programming-toolkit/pull/3). Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [maintainer guide](docs/MAINTAINERS.md).

Test locally:

```sh
python -m pip install -e '.[test]'
python -m unittest discover -s tests -v
python -m compileall -q src tests
ruff check .  # optional local development tool; installed by CI
```

GitHub Actions runs these checks on Python 3.11, 3.12, and 3.13.

## Roadmap

- **v0.1.0:** Strict plan validation, volume summaries, CLI and safe CSV output (implemented).
- **Unreleased:** CSV compatibility fixtures and byte-exact regression tests (implemented after v0.1.0).
- **Unreleased:** JSON Schema 2020-12, cross-validator fixtures and explicit parity limits.
- **v0.2 research:** Evaluation of practical adapters.
- **Future proposals:** Data adapters based on evidenced demand, plus Portuguese-Brazilian usage examples.

Read the [changelog](CHANGELOG.md), [security policy](SECURITY.md) and [release notes](docs/RELEASE_NOTES_v0.1.0.md).

## License

[MIT](LICENSE).
