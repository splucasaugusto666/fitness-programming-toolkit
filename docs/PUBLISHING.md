# Publication checklist (instructions only; nothing executed)

Publication requires the account owner's explicit approval.

1. Review source code and any company intellectual property concerns.
2. Verify GitHub access and desired repository ownership / visibility.
3. Check package name uniqueness if planning to release to PyPI.
4. Create a new public GitHub repository without importing generated fake history.
5. Create one honest initial commit with working source and documentation.
6. Push, enable GitHub Actions, verify green CI, then tag a release if appropriate.
7. Configure private vulnerability reporting, branch protection and issue templates.
8. Collect public URLs and record objective activity metrics in the eligibility dashboard.

If GitHub CLI is installed and logged in, after explicit approval and from the
`02-fitness-programming-toolkit` directory, a maintainer may use:

```sh
git init -b main
git add .
git commit -m "feat: initial fitness programming toolkit with tests"
gh repo create fitness-programming-toolkit --public --source=. --remote=origin --push
```

These are **manual commands**, not evidence of actions that have taken place.
Do not execute them before approving a repository creation.
