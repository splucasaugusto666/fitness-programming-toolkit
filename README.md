# Fitness Programming Toolkit (FPTK)

**Status:** `0.1.0` public source prototype. Not published to PyPI. No stable API guarantee.

FPTK is a small, offline Python package for checking the *structure* of strength-training
plans, summarizing their planned volume, and exporting a set-by-set CSV that a coach can
review or import into other tools. It is intended for developers, coaches and gym software
integrators who want deterministic data validation without a SaaS dependency.

## Why this exists

OpenSet, PWF and other projects address broad workout interchange. FPTK deliberately
focuses on a narrow plan template and a practical Python CLI. It does **not** claim to be
an interoperability standard, medical screening tool, AI trainer, or clinical decision aid.

## Requirements

Python 3.11+ (no runtime third-party dependencies).

## Install (local checkout)

```sh
python -m pip install -e .
```

## Try it

```sh
fptk validate examples/strength_program.json
fptk summary examples/strength_program.json
fptk export-csv examples/strength_program.json --output program.csv
```

To run without installing:

```sh
PYTHONPATH=src python -m fitness_programming_toolkit validate examples/strength_program.json
```

## Python API

```python
from fitness_programming_toolkit import read_program, summarize_program, export_csv
plan = read_program("examples/strength_program.json")
print(summarize_program(plan)["weekly_sets"])
print(export_csv(plan)[:100])
```

## Guarantees and limits

- Supports the documented `schema_version: "1.0"`; rejects unknown keys, duplicated IDs
  within their scope, control characters, booleans as numbers, NaN and infinity.
- `weeks` repeats a weekly template. The tool does not model progression,
  individual attendance or calendar dates.
- The CSV contains one row per set *per week* and prefixes formula-like text
  (`=`, `+`, `-`, `@`) so spreadsheet software does not execute it as a formula.
- Input limit: 2 MB; up to 52 weeks, 30 sessions, 50 exercises per session,
  30 sets per exercise and 5,000 weekly sets.
- Data is processed offline. No telemetry, network requests or user accounts.
- This project does **not** determine whether a plan is appropriate or safe for a person.
  Seek qualified professional guidance for individual health or injury concerns.

See [docs/FORMAT.md](docs/FORMAT.md) for the exact schema and [CONTRIBUTING.md](CONTRIBUTING.md)
for how to contribute. Test with `python -m unittest discover -s tests -v`.

## Roadmap

- v0.1: Strict schema, CLI validation, summary, safe CSV export (implemented).
- v0.2 proposal: More explicit versioned data model and machine-readable JSON Schema.
- Future research: Import/export adapters to established open standards where permitted.
- Future research: PT-BR documentation and public adoption feedback.

## License

MIT. See [LICENSE](LICENSE).
