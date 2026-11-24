# Fitness Programming Toolkit (FPTK)

**Offline Python workout plan validator, training volume calculator and streaming JSON-to-CSV exporter.**

[Português (Brasil)](docs/pt-BR.md) · [JSON Schema](schemas/program-1.0.schema.json) · [Python API](docs/API.md) · [Benchmarks](docs/BENCHMARKS.md) · [Releases](https://github.com/splucasaugusto666/fitness-programming-toolkit/releases)

[![Python CI](https://github.com/splucasaugusto666/fitness-programming-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/splucasaugusto666/fitness-programming-toolkit/actions/workflows/ci.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Latest release:** `0.1.0` (alpha; no stable public API guarantee). The default branch includes unreleased improvements. **Distribution:** GitHub source only, not PyPI.

FPTK is a small, offline Python package for **structural validation of strength-training plan data**, deterministic volume summaries, and streaming, set-by-set CSV exports with spreadsheet formula-injection mitigation. It is for developers, coaches and gym software integrators who want auditable data processing without a SaaS dependency.

It does **not** assess exercise safety, prescribe appropriate loads, measure outcomes, manage patients, or provide medical advice.

## Why use FPTK?

- **Workout JSON validation:** versioned schema, explicit limits and Python validation of aggregate counts and ID uniqueness.
- **Training volume:** exact planned sets and repetitions per week or across a program; no physiological effectiveness claims.
- **JSON to CSV:** deterministic UTF-8/CRLF output, streaming CLI export, and staged publication to protect an existing file against pre-publication write failures.
- **Offline gym software integration:** standard-library runtime, no network requirement or telemetry.

The [reproducible benchmark](docs/BENCHMARKS.md) compares buffered and streaming export on 260,000 data rows. In one local measurement, both outputs had identical SHA-256 hashes, while peak traced Python allocations fell from 60,949,235 to 157,613 bytes. This is not total process memory or a competitor benchmark.

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

## Python example: validate and export a workout plan

```python
from fitness_programming_toolkit import read_program, summarize_program, write_csv

program = read_program("examples/strength_program.json")
print(summarize_program(program)["planned_sets"])  # 28
with open("program-api.csv", "x", encoding="utf-8", newline="") as output:
    write_csv(program, output)
```

This example uses the default branch's unreleased streaming API. The caller owns the stream; use the CLI for staged file publication. See [API reference](docs/API.md) and [filesystem limitations](docs/QUICKSTART.md).

## JSON Schema for AI agents and offline integrations

The unreleased default branch includes the versioned schema in the installed
Python package. Retrieve it without downloading any external resources:

```sh
fptk schema > workout-schema.json
```

```python
from fitness_programming_toolkit import get_program_schema, parse_program

schema = get_program_schema()  # structural contract, Draft 2020-12
# Validate any generated workout dictionary with parse_program(payload).
```

This is a provider-independent data contract, not a native integration with any
particular LLM or a guarantee that every structured-output API supports all schema
keywords. FPTK still validates all generated data before use.

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

## Frequently asked questions

**Is this a workout generator?** No. It validates existing structured workout plans and computes planned counts.

**Can I import Hevy, Strong, OpenSet or openweight files directly?** Not currently. FPTK uses its own versioned format. See the [competitive baseline](docs/COMPETITIVE_BASELINE.md) for interoperability research.

**Does it work offline?** Yes. The runtime has no third-party dependencies and makes no network requests.

**Can I use it for a Brazilian gym application?** Yes, for supported structural data operations. See the [Portuguese integration example](docs/pt-BR.md). Do not treat validation as clinical or training advice.

## Contribute

Contributions are welcome, but **measurable utility matters more than commit counts**. Start by reproducing a bug or proposing an integration you actually need. The [JSON Schema issue #1](https://github.com/splucasaugusto666/fitness-programming-toolkit/issues/1) tracks the structural precheck. [Issue #2 (CSV fixtures)](https://github.com/splucasaugusto666/fitness-programming-toolkit/issues/2) was completed by [PR #3](https://github.com/splucasaugusto666/fitness-programming-toolkit/pull/3). Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [maintainer guide](docs/MAINTAINERS.md).

Test locally:

```sh
python -m pip install -e '.[test]'
python -m unittest discover -s tests -v
python -m compileall -q src tests
ruff check .  # optional local development tool; installed by CI
```

GitHub Actions tests Linux on Python 3.11, 3.12 and 3.13, plus Windows and macOS on Python 3.13. The distribution job checks the source archive, wheel metadata, and an offline wheel installation with the documented CLI outputs. See [distribution verification](docs/DISTRIBUTION.md).

## Roadmap

- **v0.1.0:** Strict plan validation, volume summaries, CLI and safe CSV output (implemented).
- **Unreleased:** CSV compatibility fixtures and byte-exact regression tests (implemented after v0.1.0).
- **Unreleased:** JSON Schema 2020-12, cross-validator fixtures and explicit parity limits.
- **v0.2 research:** Evaluation of practical adapters.
- **Unreleased:** Streaming CSV, staged file publication and Brazilian Portuguese integration example.
- **Future proposals:** Data adapters based on evidenced demand.

Read the [changelog](CHANGELOG.md), [security policy](SECURITY.md) and [release notes](docs/RELEASE_NOTES_v0.1.0.md).

## License

[MIT](LICENSE).
