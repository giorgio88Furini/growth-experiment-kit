import contextlib
import io
import json
import unittest

from growth_experiment_kit.cli import main


class CliTests(unittest.TestCase):
    def run_cli(self, argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = main(argv)
            except SystemExit as exc:
                code = exc.code
        return code, stdout.getvalue(), stderr.getvalue()

    def test_plan_human_output(self):
        code, out, _ = self.run_cli(["plan", "--control-rate", "0.10", "--mde", "0.02"])
        self.assertEqual(code, 0)
        self.assertIn("3,841 per arm", out)
        self.assertIn("absolute", out)
        self.assertIn("Warnings:", out)

    def test_analyze_json(self):
        code, out, _ = self.run_cli([
            "analyze", "--control-conversions", "100", "--control-visitors", "1000",
            "--treatment-conversions", "120", "--treatment-visitors", "1000", "--json",
        ])
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertAlmostEqual(payload["absolute_uplift"], 0.02)
        self.assertIn("p_value_two_sided", payload)

    def test_invalid_input_has_friendly_error(self):
        code, _, err = self.run_cli(["plan", "--control-rate", "1.2", "--mde", "0.02"])
        self.assertEqual(code, 2)
        self.assertIn("control_rate", err)
        self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
