"""Mirror the two split notebooks from one exact CodeRepo revision."""
import argparse
import hashlib
import json
from pathlib import Path

import sync_benchmark_notebook as mirror

NAMES = ("arxiv_nhom1_only_v1_benchmark.ipynb", "arxiv_nhom1_multi_version_benchmark.ipynb")
ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code-repo", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--repository", default="hcmus-arxiv-nhom1/CodeRepo")
    args = parser.parse_args()
    for name in NAMES:
        mirror.SOURCE = f"src/notebooks/{name}"
        mirror.TARGET = ROOT / "m1" / name
        mirror.sync(args.code_repo, args.revision, repository=args.repository)
        # Notebook cell IDs from the shared ancestor collide across both pages in
        # MyST's project-wide references. IDs do not participate in cells_digest.
        notebook = json.loads(mirror.TARGET.read_text(encoding="utf-8"))
        prefix = hashlib.sha256(name.encode()).hexdigest()[:8]
        for index, cell in enumerate(notebook["cells"]):
            cell["id"] = f"{prefix}-{index:04d}"
        mirror.TARGET.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
