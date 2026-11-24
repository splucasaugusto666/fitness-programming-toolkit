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
