# Synthetic examples

All figures here are fabricated for demonstration and are not customer or production data.

From the repository root, without installing the package:

```console
PYTHONPATH=src python -m growth_experiment_kit plan --control-rate 0.10 --mde 0.02
PYTHONPATH=src python -m growth_experiment_kit analyze --control-conversions 100 --control-visitors 1000 --treatment-conversions 120 --treatment-visitors 1000 --json
```

The count example is also recorded in `synthetic_conversion_counts.csv`. The CSV is an illustration of the input data shape; the CLI accepts counts as options rather than reading a file.
