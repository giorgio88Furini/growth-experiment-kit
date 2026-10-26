import math
import unittest

from growth_experiment_kit import InputValidationError, analyze_binary, plan_sample_size


class PlanTests(unittest.TestCase):
    def test_known_example(self):
        result = plan_sample_size(0.10, 0.02, alpha=0.05, power=0.80)
        self.assertEqual(result.sample_size_per_arm, 3841)
        self.assertEqual(result.total_sample_size, 7682)
        self.assertAlmostEqual(result.relative_mde, 0.2)
        self.assertAlmostEqual(result.treatment_rate_assumed, 0.12)
        self.assertTrue(result.warnings)

    def test_higher_power_needs_no_fewer_observations(self):
        lower = plan_sample_size(0.10, 0.02, power=0.80)
        higher = plan_sample_size(0.10, 0.02, power=0.90)
        self.assertGreater(higher.sample_size_per_arm, lower.sample_size_per_arm)

    def test_invalid_plan_values(self):
        cases = [
            ((0.0, 0.01), "control_rate"),
            ((1.0, 0.01), "control_rate"),
            ((0.10, 0.0), "absolute_mde"),
            ((0.99, 0.01), "must be less than 1"),
            ((0.10, 0.02, 1.0), "alpha"),
            ((0.10, 0.02, 0.05, 1.0), "power"),
            ((0.10, float("nan")), "absolute_mde"),
        ]
        for args, message in cases:
            with self.subTest(args=args), self.assertRaisesRegex(InputValidationError, message):
                plan_sample_size(*args)


class AnalysisTests(unittest.TestCase):
    def test_known_difference_and_interval(self):
        result = analyze_binary(100, 1000, 120, 1000)
        self.assertAlmostEqual(result.control_rate, 0.10)
        self.assertAlmostEqual(result.treatment_rate, 0.12)
        self.assertAlmostEqual(result.absolute_uplift, 0.02)
        self.assertAlmostEqual(result.relative_uplift, 0.20)
        self.assertGreater(result.z_statistic, 0)
        self.assertGreater(result.p_value_two_sided, 0)
        self.assertLess(result.p_value_two_sided, 1)
        low, high = result.confidence_interval_absolute_uplift
        self.assertLess(low, result.absolute_uplift)
        self.assertGreater(high, result.absolute_uplift)
        self.assertEqual(result.confidence_level, 0.95)

    def test_zero_control_rate_has_undefined_relative_uplift(self):
        result = analyze_binary(0, 100, 3, 100)
        self.assertIsNone(result.relative_uplift)
        self.assertTrue(any("undefined" in warning for warning in result.warnings))

    def test_zero_variance_edge_has_defined_p_value(self):
        result = analyze_binary(0, 100, 0, 150)
        self.assertEqual(result.z_statistic, 0.0)
        self.assertEqual(result.p_value_two_sided, 1.0)
        self.assertEqual(result.confidence_interval_absolute_uplift, (0.0, 0.0))

    def test_depletion_edge_and_sparse_warning(self):
        result = analyze_binary(1, 10, 0, 10)
        self.assertEqual(result.absolute_uplift, -0.1)
        self.assertTrue(any("below 5" in warning for warning in result.warnings))

    def test_invalid_analysis_values(self):
        cases = [
            ((-1, 10, 1, 10), "control_conversions"),
            ((1, 0, 1, 10), "control_visitors"),
            ((11, 10, 1, 10), "cannot exceed"),
            ((1, 10, 1.0, 10), "treatment_conversions"),
            ((True, 10, 1, 10), "control_conversions"),
            ((0, 10, 1, -10), "treatment_visitors"),
        ]
        for args, message in cases:
            with self.subTest(args=args), self.assertRaisesRegex(InputValidationError, message):
                analyze_binary(*args)

    def test_json_ready_dict(self):
        result = analyze_binary(10, 100, 12, 100).to_dict()
        self.assertIsInstance(result["warnings"], list)
        self.assertIsInstance(result["confidence_interval_absolute_uplift"], list)
        self.assertTrue(math.isfinite(result["p_value_two_sided"]))


if __name__ == "__main__":
    unittest.main()
