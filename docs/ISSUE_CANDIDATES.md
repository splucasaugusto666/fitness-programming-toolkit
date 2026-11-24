# Issue candidates (not opened on GitHub)

## 1. Add published, versioned machine-readable schema

**Problem:** Existing program validation is only accessible through Python CLI/API.
**Evidence:** `core.py` contains hand-coded rules; no JSON Schema document exists.
**Acceptance criteria:** A JSON Schema 2020-12 describes all supported fields, rejects unknown keys, and agrees with Python validation on a shared fixture suite. Do not introduce incompatible validation silently.

## 2. Interoperability feasibility investigation

**Problem:** Users of OpenSet and Portable Workout Format cannot directly import/export.
**Evidence:** `examples/strength_program.json` uses the local 1.0 format.
**Acceptance criteria:** document mapping coverage and unavoidable information loss using small public test fixtures; implement only after community feedback and licensing review.

## 3. Add deterministic CSV contract tests

**Problem:** Spreadsheet consumers need stable columns and encoding behavior.
**Evidence:** `COLUMNS` is currently defined in `core.py`.
**Acceptance criteria:** golden fixtures for quoting, Unicode, optional values and order; reject formula injection in leading ASCII whitespace while keeping trimmed field policy.
