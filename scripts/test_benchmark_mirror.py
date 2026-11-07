"""Protect generated code against accidental edits, including CI without CodeRepo."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import check_benchmark_notebook as checker
import sync_benchmark_notebook as syncer


class MirrorIntegrityTest(unittest.TestCase):
    def test_mirror_links_to_the_repository_holding_the_notebook_revision(self):
        fake_notebook = {"cells": [], "metadata": {}}
        sha = "a" * 40
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "mirror.ipynb"
            with patch.object(syncer, "TARGET", target), patch.object(
                syncer.subprocess, "check_output", side_effect=[sha, json.dumps(fake_notebook).encode()]
            ):
                syncer.sync(Path(directory), "HEAD", repository="fork/CodeRepo")
            result = json.loads(target.read_text(encoding="utf-8"))
            assert result["metadata"]["benchmark_source"]["repository"] == "fork/CodeRepo"
            assert "github.com/fork/CodeRepo/blob/" in "".join(result["cells"][0]["source"])

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
