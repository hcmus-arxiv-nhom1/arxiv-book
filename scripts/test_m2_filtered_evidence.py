import json
import unittest
from pathlib import Path


class FilteredM2EvidenceTest(unittest.TestCase):
    def test_filtered_evidence_reconciles_with_original(self):
        root = Path(__file__).resolve().parents[1] / "data" / "m2"
        load = lambda name: json.loads((root / name).read_text(encoding="utf8"))
        before, after = load("check_tables.json"), load("filtered_qa.json")
        filtered, identity = load("filter_report.json"), load("filtered_identity.json")
        self.assertEqual(identity["run_id"], "m2-full-01")
        self.assertEqual(filtered["removed_roots"], 1450)
        self.assertEqual(filtered["shards"], 200)
        self.assertTrue(before["ok"] and after["ok"])
        self.assertEqual(after["papers"], 20000)
        self.assertEqual(after["versions"], 25041)
        for key in ("elements", "hierarchy"):
            self.assertEqual(before["rows"][key] - after["rows"][key], 1450)
        self.assertEqual(before["rows"]["bibtex"], after["rows"]["bibtex"])
        self.assertEqual(before["versions"], 26491)


if __name__ == "__main__":
    unittest.main()
