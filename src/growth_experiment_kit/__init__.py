"""Transparent planning and analysis for simple conversion experiments."""

from .stats import (
    AnalysisResult,
    InputValidationError,
    PlanResult,
    analyze_binary,
    plan_sample_size,
)

__all__ = [
    "AnalysisResult",
    "InputValidationError",
    "PlanResult",
    "analyze_binary",
    "plan_sample_size",
]

__version__ = "1.0.0"
