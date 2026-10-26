"""Statistical routines for simple, two-arm conversion experiments.

These routines implement normal-approximation methods; they do not address
sequential monitoring, multiplicity, clustering, or causal identification.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from statistics import NormalDist
from typing import Any


_NORMAL = NormalDist()
_Z_975 = _NORMAL.inv_cdf(0.975)


class InputValidationError(ValueError):
    """Raised when an experiment input is outside the supported domain."""


def _finite_number(name: str, value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputValidationError(f"{name} must be a finite number.")
    result = float(value)
    if not math.isfinite(result):
        raise InputValidationError(f"{name} must be a finite number.")
    return result


def _rate(name: str, value: Any, *, open_interval: bool = False) -> float:
    result = _finite_number(name, value)
    valid = 0.0 < result < 1.0 if open_interval else 0.0 <= result <= 1.0
    if not valid:
        bounds = "strictly between 0 and 1" if open_interval else "between 0 and 1 inclusive"
        raise InputValidationError(f"{name} must be {bounds}.")
    return result


def _count(name: str, value: Any, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InputValidationError(f"{name} must be an integer.")
    if value < minimum:
        raise InputValidationError(f"{name} must be at least {minimum}.")
    return value


@dataclass(frozen=True)
class PlanResult:
    """Equal-allocation per-arm sample-size estimate and its assumptions."""

    control_rate: float
    treatment_rate_assumed: float
    absolute_mde: float
    relative_mde: float
    alpha: float
    power: float
    sample_size_per_arm: int
    total_sample_size: int
    method: str = "two-sided normal approximation for two independent proportions"
    warnings: tuple[str, ...] = (
        "This is an approximation for independent observations, equal allocation, and a fixed-horizon design.",
        "It does not adjust for multiple testing, repeated peeking, clustering, attrition, or unequal allocation.",
        "The assumed treatment rate is the planning alternative, not a forecast or a guarantee of detectable impact.",
    )

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["warnings"] = list(self.warnings)
        return result


@dataclass(frozen=True)
class AnalysisResult:
    """Descriptive effect estimates and a pooled two-sided z-test."""

    control_conversions: int
    control_visitors: int
    treatment_conversions: int
    treatment_visitors: int
    control_rate: float
    treatment_rate: float
    absolute_uplift: float
    relative_uplift: float | None
    z_statistic: float
    p_value_two_sided: float
    confidence_level: float
    confidence_interval_absolute_uplift: tuple[float, float]
    method: str = "pooled two-sided two-proportion z-test; unpooled Wald confidence interval"
    warnings: tuple[str, ...] = (
        "Results describe an observed difference and do not establish causality; valid randomization and implementation matter.",
        "The z-test and Wald interval use large-sample normal approximations and may be unreliable with sparse counts.",
        "The analysis assumes independent observations, a fixed-horizon design, and no multiple-testing, peeking, or clustering adjustment.",
    )

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["warnings"] = list(self.warnings)
        result["confidence_interval_absolute_uplift"] = list(self.confidence_interval_absolute_uplift)
        return result


def plan_sample_size(
    control_rate: float,
    absolute_mde: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> PlanResult:
    """Estimate equal per-arm sample size for a two-sided two-proportion test.

    ``absolute_mde`` is an absolute percentage-point difference expressed as a
    proportion (for example, 0.02 means two percentage points). The planning
    alternative is control rate plus the MDE.
    """
    p1 = _rate("control_rate", control_rate, open_interval=True)
    delta = _finite_number("absolute_mde", absolute_mde)
    if delta <= 0.0:
        raise InputValidationError("absolute_mde must be greater than 0.")
    p2 = p1 + delta
    if p2 >= 1.0:
        raise InputValidationError(
            "control_rate + absolute_mde must be less than 1; the assumed treatment rate must be a valid probability."
        )
    alpha_value = _finite_number("alpha", alpha)
    if not 0.0 < alpha_value < 1.0:
        raise InputValidationError("alpha must be strictly between 0 and 1.")
    power_value = _finite_number("power", power)
    if not 0.0 < power_value < 1.0:
        raise InputValidationError("power must be strictly between 0 and 1.")

    p_bar = (p1 + p2) / 2.0
    z_alpha = _NORMAL.inv_cdf(1.0 - alpha_value / 2.0)
    z_power = _NORMAL.inv_cdf(power_value)
    numerator = (
        z_alpha * math.sqrt(2.0 * p_bar * (1.0 - p_bar))
        + z_power * math.sqrt(p1 * (1.0 - p1) + p2 * (1.0 - p2))
    ) ** 2
    per_arm = math.ceil(numerator / (delta * delta))
    if per_arm < 1:
        per_arm = 1
    return PlanResult(
        control_rate=p1,
        treatment_rate_assumed=p2,
        absolute_mde=delta,
        relative_mde=delta / p1,
        alpha=alpha_value,
        power=power_value,
        sample_size_per_arm=per_arm,
        total_sample_size=2 * per_arm,
    )


def analyze_binary(
    control_conversions: int,
    control_visitors: int,
    treatment_conversions: int,
    treatment_visitors: int,
) -> AnalysisResult:
    """Analyze independent binomial arms; treatment minus control is the effect.

    The p-value comes from a pooled, two-sided score z-test. The confidence
    interval is the unpooled Wald interval at 95% confidence and is not clipped
    to the feasible [-1, 1] effect range.
    """
    c_success = _count("control_conversions", control_conversions)
    c_total = _count("control_visitors", control_visitors, minimum=1)
    t_success = _count("treatment_conversions", treatment_conversions)
    t_total = _count("treatment_visitors", treatment_visitors, minimum=1)
    if c_success > c_total:
        raise InputValidationError("control_conversions cannot exceed control_visitors.")
    if t_success > t_total:
        raise InputValidationError("treatment_conversions cannot exceed treatment_visitors.")

    p1 = c_success / c_total
    p2 = t_success / t_total
    diff = p2 - p1
    pooled = (c_success + t_success) / (c_total + t_total)
    pooled_variance = pooled * (1.0 - pooled) * (1.0 / c_total + 1.0 / t_total)
    if pooled_variance == 0.0:
        # With a pooled rate of exactly 0 or 1, both observed rates are equal.
        z_value = 0.0
        p_value = 1.0
    else:
        z_value = diff / math.sqrt(pooled_variance)
        p_value = math.erfc(abs(z_value) / math.sqrt(2.0))

    unpooled_se = math.sqrt(
        p1 * (1.0 - p1) / c_total + p2 * (1.0 - p2) / t_total
    )
    margin = _Z_975 * unpooled_se
    relative = diff / p1 if p1 > 0.0 else None
    notes = list(AnalysisResult.__dataclass_fields__["warnings"].default)
    expected = (
        c_total * pooled,
        c_total * (1.0 - pooled),
        t_total * pooled,
        t_total * (1.0 - pooled),
    )
    if min(expected) < 5.0:
        notes.append(
            "At least one expected pooled success/failure count is below 5; normal-approximation inference may be especially unreliable."
        )
    if relative is None:
        notes.append("Relative uplift is undefined because the observed control conversion rate is zero.")

    return AnalysisResult(
        control_conversions=c_success,
        control_visitors=c_total,
        treatment_conversions=t_success,
        treatment_visitors=t_total,
        control_rate=p1,
        treatment_rate=p2,
        absolute_uplift=diff,
        relative_uplift=relative,
        z_statistic=z_value,
        p_value_two_sided=p_value,
        confidence_level=0.95,
        confidence_interval_absolute_uplift=(diff - margin, diff + margin),
        warnings=tuple(notes),
    )
