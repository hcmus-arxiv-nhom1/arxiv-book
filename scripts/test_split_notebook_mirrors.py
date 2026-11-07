"""Protect both operational notebook mirrors and their Book integration."""
import json
import unittest
from pathlib import Path

import check_benchmark_notebook as checker

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("arxiv_nhom1_only_v1_benchmark.ipynb", "arxiv_nhom1_multi_version_benchmark.ipynb")


class SplitMirrorsTest(unittest.TestCase):
    def test_each_mirror_is_pinned_and_never_executed(self):
        for name in NAMES:
            with self.subTest(name=name):
                notebook = json.loads((ROOT / "m1" / name).read_text(encoding="utf-8"))
                self.assertIn("skip-execution", notebook["metadata"]["tags"])
                self.assertEqual(notebook["metadata"]["benchmark_source"]["path"], f"src/notebooks/{name}")
                self.assertEqual(checker.cells_digest(notebook), notebook["metadata"]["benchmark_source"]["cells_sha256"])
                for cell in notebook["cells"]:
                    if cell["cell_type"] == "code":
                        self.assertEqual(cell["outputs"], [])
                        self.assertIsNone(cell["execution_count"])
                        self.assertIn("skip-execution", cell["metadata"]["tags"])

    def test_both_notebooks_are_in_book_toc(self):
        toc = (ROOT / "myst.yml").read_text(encoding="utf-8")
        for name in NAMES:
            self.assertIn(f"m1/{name}", toc)

    def test_cell_ids_do_not_collide_between_mirrors(self):
        first, second = [json.loads((ROOT / "m1" / name).read_text(encoding="utf-8")) for name in NAMES]
        first_ids = {c["id"] for c in first["cells"]}
        second_ids = {c["id"] for c in second["cells"]}
        self.assertFalse(first_ids & second_ids)


if __name__ == "__main__":
    unittest.main()
