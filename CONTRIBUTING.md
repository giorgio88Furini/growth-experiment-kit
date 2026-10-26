# Contributing

Thanks for helping keep this tool clear, conservative, and easy to verify. Contributions should preserve the standard-library-only runtime, Python 3.10+ support, input validation, and explicit statistical caveats. Please avoid adding network-dependent behavior or collecting experiment data.

## Before opening a change

1. Keep changes focused and document user-visible behavior.
2. Add or update tests for formulas, validation, output formatting, and edge cases.
3. Run the complete suite from the repository root:

   ```console
   PYTHONPATH=src python -m unittest discover -s tests -v
   ```

4. Exercise both CLI subcommands, including JSON output, if their behavior changes.
5. Review README and methodology text whenever statistical behavior or interpretation changes.

This project has no mandatory formatter or linter. Keep code typed, readable, dependency-free at runtime, and compatible with Python 3.10. Do not include real customer or experiment data in tests, examples, or issues. Bug reports should include the Python version, command or API call, sanitized inputs, and observed versus expected behavior.
