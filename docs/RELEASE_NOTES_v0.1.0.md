# Fitness Programming Toolkit v0.1.0 — initial public alpha

First GitHub source release of an offline Python plan-validation and CSV-export package for strength-training templates.

## Features

- Strict versioned JSON validation (`schema_version: "1.0"`), size limits, duplicate-ID and duplicate-key checks.
- Immutable Python models and deterministic planned sessions/sets/repetitions summaries.
- CLI: `fptk validate`, `fptk summary`, `fptk export-csv`.
- UTF-8 CSV with CRLF and basic spreadsheet-formula neutralization for user-controlled text.
- Synthetic sample, documentation, unit tests and automated lint across Python 3.11–3.13.

## Install from source

This package is **not published on PyPI**.

```sh
git clone https://github.com/splucasaugusto666/fitness-programming-toolkit.git
cd fitness-programming-toolkit
python -m pip install -e .
fptk validate examples/strength_program.json
```

## Limitations

The format intentionally does not model progressive overload, calendars, athlete response, client records, clinical appropriateness or exercise effectiveness. This is not an interchange standard and the alpha Python API is unstable. No independent security audit or external adoption is claimed.

## Contribute

Focused opportunities: [#1 versioned JSON Schema](https://github.com/splucasaugusto666/fitness-programming-toolkit/issues/1) and [#2 CSV golden fixtures](https://github.com/splucasaugusto666/fitness-programming-toolkit/issues/2). See [CONTRIBUTING.md](https://github.com/splucasaugusto666/fitness-programming-toolkit/blob/main/CONTRIBUTING.md). Real, reviewable improvements are preferred over activity inflation.
