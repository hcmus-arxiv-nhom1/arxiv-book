"""Check provenance and execution isolation; optionally compare exact canonical cells."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def cells_digest(notebook: dict) -> str:
    cells = [
        dict(cell_type=c["cell_type"], source=c["source"])
        for c in notebook["cells"]
        if not c["metadata"].get("generated_provenance")
    ]
    return hashlib.sha256(json.dumps(cells, sort_keys=True).encode()).hexdigest()


def check(code_repo: Path | None = None) -> None:
    path = ROOT / "m1/arxiv_nhom1_crawl_benchmark.ipynb"
    notebook = json.loads(path.read_text(encoding="utf-8"))
    assert "skip-execution" in notebook["metadata"]["tags"]
    provenance = notebook["metadata"]["benchmark_source"]
    assert re.fullmatch(r"[0-9a-f]{40}", provenance["revision"])
    assert re.fullmatch(r"[0-9a-f]{64}", provenance["sha256"])
    assert cells_digest(notebook) == provenance["cells_sha256"]
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            assert cell.get("outputs") == [] and cell.get("execution_count") is None
            assert "skip-execution" in cell.get("metadata", {}).get("tags", [])
    if code_repo:
        raw = subprocess.check_output(
            [
                "git",
                "-C",
                str(code_repo),
                "show",
                f"{provenance['revision']}:{provenance['path']}",
            ]
        )
        assert hashlib.sha256(raw).hexdigest() == provenance["sha256"]
        canonical = json.loads(raw)
        cells = [
            c
            for c in notebook["cells"]
            if not c["metadata"].get("generated_provenance")
        ]
        assert [c["source"] for c in cells] == [c["source"] for c in canonical["cells"]]
    print("Benchmark mirror: valid provenance, no outputs, execution disabled")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--code-repo", type=Path)
    check(parser.parse_args().code_repo)
