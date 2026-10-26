# Growth Experiment Kit

A small, transparent, standard-library-only Python package and CLI for planning and analyzing a **two-arm conversion-rate experiment**. It provides an equal-allocation sample-size estimate and a descriptive analysis of independent binomial arms. It does not replace an experiment design review or a statistician's judgment.

## Requirements and installation

- Python 3.10 or newer
- Runtime: Python standard library only

Install from a local checkout:

```console
python -m pip install .
```

Or run directly from the repository without installing:

```console
PYTHONPATH=src python -m growth_experiment_kit --help
```

## Plan sample size

`--control-rate` and `--mde` are proportions, not percentages: `0.10` means 10%, while `0.02` means an **absolute increase of two percentage points**. The package assumes the treatment alternative is control rate plus the MDE.

```console
growth-experiment plan --control-rate 0.10 --mde 0.02
# Equivalent without installation:
PYTHONPATH=src python -m growth_experiment_kit plan --control-rate 0.10 --mde 0.02
```

Set the two-sided type-I error rate and target power explicitly when needed:

```console
growth-experiment plan --control-rate 0.10 --mde 0.02 --alpha 0.05 --power 0.90 --json
```

The example estimates 3,841 visitors per arm (7,682 total) at alpha 0.05 and 80% power. These are approximate planning values, not a promise of significance or business impact.

## Analyze conversion counts

Pass integer conversions and visitors for each independent arm. The effect is treatment minus control:

```console
growth-experiment analyze \
  --control-conversions 100 --control-visitors 1000 \
  --treatment-conversions 120 --treatment-visitors 1000
```

The CLI reports observed rates, **absolute uplift** (a percentage-point difference), **relative uplift** (the absolute difference divided by the control rate), a pooled two-sided two-proportion z-test p-value, and an unpooled 95% Wald confidence interval for absolute uplift. For example, moving from 10% to 12% is +2 percentage points absolute and +20% relative. Relative uplift is undefined if the observed control rate is zero.

Both commands support `--json` for machine-readable output. Errors are printed in plain language and exit with a nonzero status. In Python, import `plan_sample_size`, `analyze_binary`, and `InputValidationError` from `growth_experiment_kit`.

## Method and limitations

The methods assume independent observations, equal allocation for planning, a fixed-horizon design, and normal approximations. They do not correct for multiple comparisons, repeated peeking/sequential testing, clustering, unequal allocation, attrition, covariate adjustment, or noncompliance. The analysis does not verify randomization or identify a causal effect. Sparse data may make the approximations unreliable; the CLI emits a warning when expected pooled successes or failures in any arm are below five. See [the methodology notes](docs/methodology.md) for formulas and edge cases.

Use synthetic or appropriately approved, minimized data. This tool performs no network requests and does not store experiment data.

## Development and tests

```console
PYTHONPATH=src python -m unittest discover -s tests -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution and validation guidance and [SECURITY.md](SECURITY.md) for security reporting.
