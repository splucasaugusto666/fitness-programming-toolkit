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
- String values cannot contain ASCII controls (including newlines and tabs) or isolated
  UTF-16 surrogate code points. Valid supplementary Unicode scalar characters are accepted.
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
python -m pip install -e '.[test]'
python -m unittest discover -s tests -v
```

Do not regenerate the golden CSV as part of a test. A deliberate CSV format change
requires manual review of the byte diff and compatibility implications before updating
this fixture. This test validates the exporter and CLI output only; it does not promise
interoperability with an external training-plan standard.


## JSON Schema 2020-12

The [versioned schema](../schemas/program-1.0.schema.json) validates ordinary JSON
structure before a consumer invokes the authoritative Python validator.
It has no remote references, so it can be downloaded and used offline with a
Draft 2020-12 validator. The public format version remains the string "1.0".

Python example (from the repository root):

```sh
python -m pip install -e '.[test]'
python -m json.tool schemas/program-1.0.schema.json
python -m unittest discover -s tests -v
```

```python
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from fitness_programming_toolkit import read_program

schema = json.loads(Path("schemas/program-1.0.schema.json").read_text(encoding="utf-8"))
data = json.loads(Path("examples/strength_program.json").read_text(encoding="utf-8"))
Draft202012Validator(schema).validate(data)
program = read_program("examples/strength_program.json")
```

### Explicit limits of parity

- JSON Schema checks required fields, unknown keys, bounds, per-array sizes,
  weekday values, and string length/control/trim rules. The whitespace
  pattern uses an explicit Unicode set reflecting Python's strip behavior;
  verify regex compatibility in your chosen validator.
- It does not enforce unique session IDs or exercise IDs by property across
  different objects. The Python validator does.
- It cannot express the aggregate 5,000 weekly-set limit in a straightforward
  portable structural schema. The Python validator checks the aggregate.
- JSON Schema integer semantics include numeric values such as 1.0, whereas
  the Python validator requires an actual int after parsing, and rejects
  booleans. JSON Schema operates on parsed JSON values, not their numeric spelling.
- The schema cannot enforce the original file's 2 MB byte limit, UTF-8
  encoding, JSON duplicate member names, or non-standard non-finite tokens.
  Use a strict JSON parser and the FPTK file reader for those checks. Parser-dependent
  numeric token and nesting limits can also cause decoding failures before structural
  validation. FPTK reports these as DataValidationError. The runtime rejects isolated
  surrogate code points; Unicode handling may differ between schema validators.
- Neither validator evaluates clinical or training suitability.

See [valid](../tests/fixtures/schema_valid.json) and
[invalid](../tests/fixtures/schema_invalid.json) synthetic fixtures.
The schema is a structural precheck, not a claim of full equivalence
or interoperability with another training format.
