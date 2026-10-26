"""Command-line interface for growth-experiment-kit."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .stats import InputValidationError, analyze_binary, plan_sample_size


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="growth-experiment",
        description="Plan and analyze a simple two-arm conversion experiment.",
        epilog="Use --json for machine-readable output. Statistical results rely on the documented assumptions.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="estimate equal per-arm sample size")
    plan.add_argument("--control-rate", type=float, required=True, help="baseline conversion probability, e.g. 0.10")
    plan.add_argument("--mde", type=float, required=True, help="absolute MDE as a proportion, e.g. 0.02 for 2 percentage points")
    plan.add_argument("--alpha", type=float, default=0.05, help="two-sided type-I error rate (default: 0.05)")
    plan.add_argument("--power", type=float, default=0.80, help="target statistical power (default: 0.80)")
    plan.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")

    analyze = subparsers.add_parser("analyze", help="analyze independent conversion counts")
    analyze.add_argument("--control-conversions", type=int, required=True)
    analyze.add_argument("--control-visitors", type=int, required=True)
    analyze.add_argument("--treatment-conversions", type=int, required=True)
    analyze.add_argument("--treatment-visitors", type=int, required=True)
    analyze.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")
    return parser


def _format_plan(result: dict) -> str:
    lines = [
        f"Estimated sample size: {result['sample_size_per_arm']:,} per arm ({result['total_sample_size']:,} total)",
        f"Planning rates: control {result['control_rate']:.2%}; treatment alternative {result['treatment_rate_assumed']:.2%}",
        f"MDE: {result['absolute_mde']:.2%} absolute ({result['relative_mde']:.2%} relative to control)",
        f"Design inputs: two-sided alpha {result['alpha']:.3g}; power {result['power']:.1%}",
        "Warnings:",
    ]
    lines.extend(f"  - {warning}" for warning in result["warnings"])
    return "\n".join(lines)


def _format_analysis(result: dict) -> str:
    relative = result["relative_uplift"]
    relative_text = "undefined (control rate is zero)" if relative is None else f"{relative:+.2%}"
    low, high = result["confidence_interval_absolute_uplift"]
    lines = [
        f"Observed conversion: control {result['control_rate']:.2%} ({result['control_conversions']:,}/{result['control_visitors']:,}); "
        f"treatment {result['treatment_rate']:.2%} ({result['treatment_conversions']:,}/{result['treatment_visitors']:,})",
        f"Absolute uplift (treatment − control): {result['absolute_uplift']:+.2%} (percentage points)",
        f"Relative uplift vs control: {relative_text}",
        f"Pooled two-sided z-test: z={result['z_statistic']:.4f}, p={result['p_value_two_sided']:.6g}",
        f"Unpooled 95% Wald confidence interval for absolute uplift: [{low:+.2%}, {high:+.2%}]",
        "Warnings:",
    ]
    lines.extend(f"  - {warning}" for warning in result["warnings"])
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "plan":
            result = plan_sample_size(args.control_rate, args.mde, args.alpha, args.power).to_dict()
            formatter = _format_plan
        else:
            result = analyze_binary(
                args.control_conversions,
                args.control_visitors,
                args.treatment_conversions,
                args.treatment_visitors,
            ).to_dict()
            formatter = _format_analysis
    except InputValidationError as exc:
        parser.error(str(exc))
        return 2

    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        print(formatter(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
