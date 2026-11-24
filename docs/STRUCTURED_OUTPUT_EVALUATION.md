# Structured-output integration evaluation (proposed)

Status: planned experiment, not a completed benchmark. FPTK validates structural training-plan data; it does not evaluate exercise suitability or medical safety.

## Question

How reliably do different structured-output producers conform to the same versioned FPTK data contract, and which failures are caught by the JSON Schema precheck versus the Python runtime?

## Method

- Freeze a version of the schema and runtime at a recorded Git commit.
- Assemble synthetic valid and invalid cases, including duplicate IDs, aggregate limits, unexpected fields, malformed JSON and boundary values. Derive expected outcomes from the documented contract before running the test.
- Use the existing [format rules](FORMAT.md), [API contract](API.md) and [AI integration guide](AI_INTEGRATIONS.md). Distinguish provider-specific schema transformations from the canonical schema.
- Compare a local JSON Schema validator with the FPTK runtime first. Then, if authorized and available, separately evaluate model-generated outputs with fixed prompts and recorded model identifiers, tool settings, sample counts and dates.
- Never send actual patient or client information. Do not claim provider certification or use an API that incurs unapproved cost.

## Metrics

Report exact expected-outcome agreement, false acceptance, false rejection, parse failures and runtime/schema disagreement by case category. For generated outputs, report both first-attempt and post-repair acceptance with explicit denominators, plus latency and cost only if measured. Publish reproducible synthetic cases and negative results. Do not merge generated-output and hand-authored fixture results into a single accuracy number.

## Existing evidence and limits

The repository already documents deterministic exports and a [streaming benchmark](BENCHMARKS.md) with identical output hashes. That benchmark is about Python allocations and output consistency, not model quality. This new protocol would evaluate data-contract conformance, not the effectiveness of generated workout prescriptions. No new experimental results are claimed here.
