# Maintainer release procedure

The public GitHub repository is `splucasaugusto666/fitness-programming-toolkit`. The initial commits and CI passing Python 3.11–3.13 were verified before this release.

## Initial release `v0.1.0`

Release notes live in [RELEASE_NOTES_v0.1.0.md](RELEASE_NOTES_v0.1.0.md). The GitHub prerelease is created by a narrowly scoped one-off Action when the maintainer-authorized `release/v0.1.0` branch is pushed, after lint and tests. Review the final release link, target commit and status on GitHub.

This is a **source-only GitHub release**. No PyPI account is touched, no software downloads are claimed, and no users are enrolled.

## Later versions

1. Obtain maintainer approval for the version and release scope.
2. Update changelog and notes; review security and compatibility.
3. Run lint, tests and CLI smoke checks on supported Python versions.
4. Create a tag and release from the reviewed commit; check the actual tag and CI.
5. Record verified issue and PR outcomes; do not inflate adoption metrics.

Retire the one-off release workflow after `v0.1.0` and review any general release automation separately.
