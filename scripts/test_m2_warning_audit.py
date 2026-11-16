import json
import unittest
from pathlib import Path


class M2WarningAuditTest(unittest.TestCase):
    def test_scope_and_reachability(self):
        base = Path(__file__).resolve().parents[1] / "data" / "m2"
        rows = [json.loads(x) for x in (base / "tex_warning_reachability.jsonl").read_text(encoding="utf8").splitlines()]
        self.assertEqual(len(rows), 48)
        self.assertTrue(all(r["status"] == "checked" and r["same_root"] for r in rows))
        self.assertEqual(sum(len(r["warning_paths"]) for r in rows), 69)
        self.assertEqual(sum(len(r["reachable_warnings"]) for r in rows), 67)
        verified = [r for r in rows if r["hash_verified"]]
        self.assertEqual(len(verified), 27)
        self.assertEqual(sum(len(r["warning_paths"]) for r in verified), 42)
        self.assertEqual(sum(len(r["reachable_warnings"]) for r in verified), 40)


if __name__ == "__main__":
    unittest.main()
