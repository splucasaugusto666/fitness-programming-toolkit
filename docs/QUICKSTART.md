# Getting started with FPTK

The example in this repository is synthetic. Do not commit real client health records or personal information.

## Install from the repository

```sh
git clone https://github.com/splucasaugusto666/fitness-programming-toolkit.git
cd fitness-programming-toolkit
python -m pip install -e .
```

Python 3.11+ is supported; no third-party runtime dependencies are required.

## Check a plan and view a summary

```sh
fptk validate examples/strength_program.json
fptk summary examples/strength_program.json
```

The validation command prints `VALID: demo-strength-01 (schema 1.0)`. The unchanged sample has 2 weekly sessions, 7 weekly sets and 68 planned reps, repeated for 4 weeks: 8 planned sessions, 28 planned sets and 272 planned reps in total. These numbers count planned data only; they are not measures of effectiveness or medical safety.

## Export CSV

```sh
fptk export-csv examples/strength_program.json --output program.csv
```

The sample produces 28 data rows and a fixed 13-column header. UTF-8 CSV uses CRLF line endings; formula-like user text is prefixed with an apostrophe. An existing output file is preserved unless you pass `--force`. This is a defensive measure and not a guarantee for every spreadsheet program.

## Use the Python interface

```python
from fitness_programming_toolkit import read_program, summarize_program, export_csv
plan = read_program('examples/strength_program.json')
assert summarize_program(plan)['planned_sets'] == 28
csv_text = export_csv(plan)
assert csv_text.startswith('program_id,program_title,week,')
```

See [API.md](API.md) for the exported functions and [FORMAT.md](FORMAT.md) for schema requirements.

## Run checks

Install the test extra and lint tool before running the full developer suite.

```sh
python -m pip install -e '.[test]' ruff
python -m unittest discover -s tests -v
python -m compileall -q src tests
ruff check .  # development tool; installed by CI
```

Please report reproductions without personal information in [GitHub Issues](https://github.com/splucasaugusto666/fitness-programming-toolkit/issues).
