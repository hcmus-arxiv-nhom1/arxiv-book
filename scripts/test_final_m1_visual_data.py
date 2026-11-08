import importlib.util
import tempfile
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location("collect_final_m1", Path(__file__).with_name("collect_final_m1.py"))
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class FinalVisualizationDataTests(unittest.TestCase):
    def test_reference_denominators_are_distinct_and_zero_is_unknown(self):
        rows = [{"ref_status": "ok", "n_refs_total": "2", "n_refs_meta_ok": "1", "n_refs_meta_complete": "1"},
                {"ref_status": "not_found", "n_refs_total": "0", "n_refs_meta_ok": "0", "n_refs_meta_complete": "0"}]
        statuses, meta = collector.reference_summary("run", rows)
        self.assertEqual({x["status"]: x["papers"] for x in statuses}, {"ok": 1, "not_found": 1})
        self.assertEqual((meta["references"], meta["with_s2_id"], meta["complete_metadata"]), (2, 1, 1))
        _, empty = collector.reference_summary("run", [dict(rows[1])])
        self.assertEqual(empty["references"], 0)
        self.assertIsNone(empty["s2_id_pct"])

    def test_timeline_rejects_missing_or_empty_required_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "timeline.csv"
            path.write_text("minute_utc,n_429,n_5xx,backoff_s\n2026-11-06 01:13,2,0,3.0\n", encoding="utf8")
            rows = collector.timeline_rows("run", path)
            self.assertEqual((rows[0]["run"], rows[0]["n_429"], rows[0]["backoff_s"]), ("run", 2, 3.0))
            path.write_text("minute_utc,n_429,n_5xx,backoff_s\n2026-11-06 01:13,,0,3.0\n", encoding="utf8")
            with self.assertRaises(ValueError):
                collector.timeline_rows("run", path)


if __name__ == "__main__":
    unittest.main()
