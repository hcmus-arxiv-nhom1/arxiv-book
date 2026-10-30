"""Protect generated code against accidental edits, including CI without CodeRepo."""

import copy
import json
import unittest
from unittest.mock import patch

import check_benchmark_notebook as checker


class MirrorIntegrityTest(unittest.TestCase):
    def test_changed_code_cell_fails_without_canonical_checkout(self):
        original = json.loads(
            (checker.ROOT / "m1/arxiv_nhom1_crawl_benchmark.ipynb").read_text()
        )
        changed = copy.deepcopy(original)
        cell = next(c for c in changed["cells"] if c["cell_type"] == "code")
        cell["source"] = ["raise RuntimeError('unrecorded edit')\n"]
        with patch.object(checker.Path, "read_text", return_value=json.dumps(changed)):
            with self.assertRaises(AssertionError):
                checker.check()


if __name__ == "__main__":
    unittest.main()
