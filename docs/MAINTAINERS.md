# Maintainer playbook

## Prioritize real software value

1. Reproducible validation defects, broken data exports and security reports.
2. Focused regression tests and backward-compatible fixes.
3. Interoperability proposals backed by specific integrator requirements.
4. Accurate documentation, language support and onboarding.

Do not create issues or PRs solely to boost contribution counts. Decline spam, copied proprietary content, customer health records and unreviewed mass-generated patches.

## Review checklist

- Reproduce the defect and verify that the change solves it.
- Confirm license provenance and input-boundary behavior.
- Require appropriate tests and documentation updates.
- Verify CI on Python 3.11, 3.12 and 3.13, including Ruff and CLI smoke tests.
- Discuss any behavior change to `schema_version: "1.0"` in advance.
- Explain the outcome publicly and respectfully without implying every PR will merge.

## Release policy

`0.1.x` is alpha, distributed as GitHub source. The one-off `v0.1.0` release workflow creates a prerelease only for the explicitly authorized release branch and only after tests pass. Future releases and PyPI uploads require separate authorization. See [PUBLISHING.md](PUBLISHING.md).

Do not infer user adoption from stars, documentation views or assistant-authored issues.
