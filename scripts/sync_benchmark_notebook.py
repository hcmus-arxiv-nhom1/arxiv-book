"""Generate the Book mirror from an exact CodeRepo commit, without executing it.

Drafted with assistance from OpenAI Codex, disclosed per course rules.
"""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from check_benchmark_notebook import cells_digest

SOURCE = "src/notebooks/arxiv_nhom1_crawl_benchmark.ipynb"
TARGET = Path(__file__).resolve().parents[1] / "m1/arxiv_nhom1_crawl_benchmark.ipynb"


def sync(repo: Path, revision: str) -> None:
    sha = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", revision], text=True
    ).strip()
    raw = subprocess.check_output(["git", "-C", str(repo), "show", f"{sha}:{SOURCE}"])
    notebook = json.loads(raw)
    metadata = notebook.setdefault("metadata", {})
    metadata["tags"] = sorted(set(metadata.get("tags", [])) | {"skip-execution"})
    metadata["benchmark_source"] = dict(
        repository="hcmus-arxiv-nhom1/CodeRepo",
        revision=sha,
        path=SOURCE,
        sha256=hashlib.sha256(raw).hexdigest(),
        cells_sha256=cells_digest(notebook),
    )
    url = f"https://github.com/hcmus-arxiv-nhom1/CodeRepo/blob/{sha}/{SOURCE}"
    colab = f"https://colab.research.google.com/github/hcmus-arxiv-nhom1/CodeRepo/blob/{sha}/{SOURCE}"
    intro = (
        ":::{note}\nThis is a generated, nonexecuting mirror of the operational notebook. "
        "The Book build never crawls arXiv or mounts Drive. Final measurements are pending.\n\n"
        f"[Open this version in Colab]({colab}) · [Canonical source]({url}) · "
        "Download notebook: {download}`./arxiv_nhom1_crawl_benchmark.ipynb`\n\n"
        f"CodeRepo notebook revision: `{sha}`. The setup cell separately pins the "
        "implementation revision used by the crawler.\n:::"
    )
    notebook["cells"].insert(
        1,
        dict(
            cell_type="markdown",
            id="book-provenance",
            metadata={"generated_provenance": True},
            source=intro.splitlines(True),
        ),
    )
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            cell["outputs"], cell["execution_count"] = [], None
            tags = cell.setdefault("metadata", {}).get("tags", [])
            cell["metadata"]["tags"] = sorted(set(tags) | {"skip-execution"})
    TARGET.write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"Generated {TARGET} from CodeRepo@{sha}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code-repo", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    sync(args.code_repo, args.revision)
