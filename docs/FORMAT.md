# FPTK plan format 1.0

Required top-level keys: `schema_version`, `program_id`, `title`, `weeks`, `sessions`.
The version literal is `"1.0"`, not a numeric version. Unknown fields are rejected.

- `program_id`: nonempty trimmed UTF-8 text, max 64 characters.
- `title`: nonempty trimmed text, max 120 characters.
- `weeks`: integer from 1 to 52 (not a boolean).
- `sessions`: 1 to 30 weekly sessions; each has `session_id` (unique across the plan),
  `name`, `day_of_week` (lowercase English weekday), and `exercises`.
- `exercises`: 1 to 50 per session. An `exercise_id` must be unique within a session;
  it can appear in another session. Each exercise has `exercise_id`, `name`, and `sets`.
- `sets`: 1 to 30 per exercise. Required `reps` is an integer 1–1000.
  Required `rest_seconds` is an integer 0–7200. Optional `load_kg` is a finite
  number 0–5000, or null. Optional `rpe` is a finite number 1–10, or null.
- String values cannot contain ASCII controls (including newlines and tabs).
- JSON numbers must be finite. The total sets in the weekly template cannot exceed 5000.

CSV columns: `program_id`, `program_title`, `week`, `session_id`, `session_name`,
`day_of_week`, `exercise_id`, `exercise_name`, `set_number`, `reps`, `load_kg`, `rpe`,
`rest_seconds`. Each week repeats the same prescribed set data. Missing optional
values are blank in CSV. Formula-like strings are prefixed with an apostrophe.

Sample file: [`examples/strength_program.json`](../examples/strength_program.json).

**Scope:** Structural validation only. `rpe` is recorded verbatim, not used to prescribe
loads. Weekday labels have no date/time semantics. This version does not track injuries,
medical conditions, personal identifiers, progression or exercise effectiveness.

## Deterministic CSV bytes (golden contract)

The tracked source fixture [`tests/fixtures/csv_contract_input.json`](../tests/fixtures/csv_contract_input.json)
contains **fictional data only**, including accents, quotes, commas, nullable values,
and formula-like strings. Its expected output is committed as
[`tests/fixtures/csv_contract_expected.csv`](../tests/fixtures/csv_contract_expected.csv).

A byte-for-byte regression test compares `export_csv(program).encode("utf-8")` and the
CLI-generated file to those expected bytes. The fixture locks the following behavior:

- UTF-8 text **without BOM**; comma separators; standard CSV double-quote escaping.
- A header of 13 columns in the order listed above, each row terminated by **CRLF**
  (`\r\n` bytes). `.gitattributes` prevents accidental line-ending conversion.
- Weeks in ascending order; within each week, sessions, exercises and sets in the
  order supplied in the source JSON. A 2-week fixture with 4 sets per week yields 8 rows.
- Missing or null `load_kg`/`rpe` are empty CSV cells. Present numbers serialize in
  Python's usual representation (`12.5`, `0.0`, `1.0`).
- Text that starts (after left whitespace) with the ASCII characters `=`, `+`, `-`
  or `@` is prefixed with a literal apostrophe to reduce common spreadsheet formula
  injection risks. A quoted CSV field is **not**, by itself, an injection defense.

**Security limitation:** The apostrophe prefix is a defense-in-depth mitigation for
common spreadsheet software, not a guarantee for all CSV import modes, spreadsheet
products or other Unicode formula triggers. Consumers must apply their own escaping
and trust policy. No spreadsheet formula is evaluated by the test suite.

Run the contract tests with:

```sh
python -m unittest discover -s tests -v
```

Do not regenerate the golden CSV as part of a test. A deliberate CSV format change
requires manual review of the byte diff and compatibility implications before updating
this fixture. This test validates the exporter and CLI output only; it does not promise
interoperability with an external training-plan standard.
