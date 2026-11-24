# Contributing

We welcome reproductions of real bugs, regression tests and interoperability proposals.
Before working on a significant change, open an issue to discuss the user problem and
expected behavior. **No issue or PR is guaranteed acceptance.**

1. Fork the repository and create a topic branch.
2. Use Python 3.11+; `python -m pip install -e .`.
3. Run `python -m unittest discover -s tests -v` and `python -m compileall -q src tests`.
4. When adding a rule, provide a failing test and a precise error message.
5. Keep runtime free of remote requests; do not include clients' health data.
6. Describe changes, compatibility implications and test output in the PR.

No AI-generated PR flooding, artificial contribution exchange, or deceptive metrics.
Contributions are reviewed for maintainability, originality and fitness for purpose.
