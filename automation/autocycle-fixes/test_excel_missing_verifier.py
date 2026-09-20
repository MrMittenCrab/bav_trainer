"""Characterize unresolved-verifier recovery without live providers or Excel.

Usage: python test_excel_missing_verifier.py /path/to/excel_verification.py
This deliberately tests refusal, not successful BAV cached-value verification.
"""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

excel = None


class MissingVerifierTests(unittest.TestCase):
    def setUp(self):
        if excel is None:
            self.skipTest("Run this harness with an explicit AutoCycle helper path")

    def test_unidentified_verifier_blocks_before_excel_and_preserves_state(self):
        # Removing the resolver-action rejection must fail this test: no fallback
        # command, Excel invocation, or successful return is allowed.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.xlsx"
            source.write_bytes(b"untouched workbook")
            cache = root / "current-review"
            review = (
                "REVIEW_STATUS: BLOCKED\n"
                "BLOCKER_KEY: excel-cached-value-verification\n"
                "REVIEW: Required cached-value verification unavailable\n"
                "HUMAN_ACTION: STALE instruction to manually recalculate\n"
            )
            cache.write_text(review)
            reason = (
                "No existing read-only verifier checks independent references, "
                "formula preservation, and cached errors in dependencies."
            )

            def resolve(args, **kwargs):
                self.assertIn("--sandbox", args)
                self.assertEqual(args[args.index("--sandbox") + 1], "read-only")
                answer = Path(args[args.index("--output-last-message") + 1])
                answer.write_text(json.dumps({"action": reason}))
                return subprocess.CompletedProcess(args, 0, "", "")

            output = io.StringIO()
            with (
                patch("adjudication.location", return_value=root),
                patch.object(excel.subprocess, "run", side_effect=resolve),
                patch.object(excel, "verify", side_effect=AssertionError(
                    "Must not recalculate without a valid verifier"
                )),
                contextlib.redirect_stdout(output),
            ):
                self.assertEqual(excel.resume_blocker(cache), 2)

            self.assertIn(reason, output.getvalue())
            self.assertNotIn("STALE", output.getvalue())
            self.assertEqual(source.read_bytes(), b"untouched workbook")
            self.assertEqual(cache.read_text(), review)
            results = list(root.glob("excel-resume-*/result.json"))
            self.assertEqual(len(results), 1)
            result = json.loads(results[0].read_text())
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(result["action"], reason)
            self.assertEqual(list(root.glob("excel-verification-*")), [])


if __name__ == "__main__":
    helper = Path(sys.argv.pop(1)).resolve(strict=True)
    sys.path.insert(0, str(helper.parent))
    spec = importlib.util.spec_from_file_location("excel_verification", helper)
    excel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(excel)
    unittest.main()
