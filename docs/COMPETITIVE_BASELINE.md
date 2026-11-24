# Competitive engineering baseline

Public documentation reviewed on 2026-11-23. This is a capability comparison,
not a performance ranking. We have not executed the other projects.

| Project | Documented strengths | FPTK response |
| --- | --- | --- |
| [OpenSet](https://openset.dev/) | Multi-sport JSON standard, extensibility, schema and validator | Prefer explicit mappings over inventing an incompatible standard. |
| [openweight](https://openweight.dev/) | Strength-training data portability, TypeScript and Kotlin SDKs | Evaluate a narrow adapter with loss reporting and round-trip tests. |
| [Open Workout](https://github.com/openexercise/open-workout) | Workout schemas, API and MCP tool profile | Evaluate machine-readable diagnostics and agent-safe interfaces. |
| [Kaiord](https://github.com/pablo-albaladejo/kaiord) | Multiple format adapters, SDK, CLI and MCP | Focus initially on strict offline Python validation and auditable export. |

FPTK has a narrower scope. Its differentiated claims must be measured: byte-exact
CSV, invalid-input handling, transactional file publication, and resource usage.
See [BENCHMARKS.md](BENCHMARKS.md) for the first measured improvement against our
own implementation. Cross-project superiority remains unproven. Before any
adapter ships, verify source licensing, versioned mapping, known information
loss and reproducible interoperability tests. Do not claim adoption without evidence.
