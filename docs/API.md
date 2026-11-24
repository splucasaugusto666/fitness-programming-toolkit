# Public Python API — 0.1.0 (experimental)

The interface may evolve before 1.0. This library validates **plan data**, not the quality, suitability, or clinical safety of a workout.

```python
from fitness_programming_toolkit import (
    DataValidationError, Program, parse_program, read_program,
    summarize_program, iter_csv_rows, export_csv, write_csv, get_program_schema,
 )
```

## Input

- `read_program(path: str | Path) -> Program`: read UTF-8 JSON (max 2 MB), reject duplicate JSON object keys and validate data; filesystem failures can raise `OSError`.
- `parse_program(payload: dict) -> Program`: parse a Python dictionary following [the 1.0 format](FORMAT.md). Although typed as a Mapping, arbitrary custom mapping classes are not guaranteed to work.
- `DataValidationError(ValueError)`: invalid data exception, with readable field paths; the message wording is not a stable machine API.

## Offline schema discovery

- `get_program_schema() -> dict`: returns a fresh copy of the bundled version 1.0
  JSON Schema (Draft 2020-12), without network access or a source checkout.
- `fptk schema`: prints the same JSON schema to stdout. This is an unreleased
  interface on the default branch, useful for tooling that needs a structured
  contract before producing workout data. It is a structural precheck, not a
  guarantee of compatibility with a specific AI provider's structured-output subset.
  Always use `parse_program` or `read_program` for authoritative validation.

## Data

`Program` and its nested `Session`, `Exercise` and `PrescriptionSet` models are frozen dataclasses. The weekly template is repeated for `weeks`. Numeric loads and RPE values are recorded as provided, not inferred or prescribed.

## Output

- `summarize_program(program) -> dict`: returns `program_id`, `title`, `weeks`, `sessions_per_week`, `weekly_sets`, `weekly_reps`, `planned_sessions`, `planned_sets` and `planned_reps`.
- `iter_csv_rows(program) -> Iterator[tuple]`: emits week/session/exercise/set rows, with no header; this is a low-level interface.
- `export_csv(program) -> str`: returns CSV text with headers, UTF-8 compatible text and CRLF; it does **not** save a file.

- `write_csv(program, stream) -> None`: incrementally writes the same header and CSV rows to a caller-owned text stream. Open disk streams with `encoding="utf-8", newline=""`; the function does not close or flush the stream and does not provide atomic publication. The CLI stages the output before publication.

## Minimal example

```python
from fitness_programming_toolkit import DataValidationError, parse_program, summarize_program
payload = {
    'schema_version': '1.0', 'program_id': 'example', 'title': 'Demo', 'weeks': 1,
    'sessions': [{'session_id': 'mon', 'name': 'Monday',
                  'day_of_week': 'monday', 'exercises': [
                      {'exercise_id': 'sq', 'name': 'Squat',
                       'sets': [{'reps': 8, 'rest_seconds': 120}]}]}]
}
try:
    plan = parse_program(payload)
    print(summarize_program(plan)['weekly_sets'])
except DataValidationError as error:
    print(f'Invalid input: {error}')
```
