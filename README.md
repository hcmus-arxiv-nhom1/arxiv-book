# arxiv-book — Group 1

> **Do not rename the organization or repository before the poster deadline.** The book URL is included in the Moodle submission; renaming it would break the link.

- Book: <https://hcmus-arxiv-nhom1.github.io/arxiv-book/>
- Code repository: <https://github.com/hcmus-arxiv-nhom1/CodeRepo>

The book uses **Jupyter Book 2** (MyST). Its configuration and table of contents are in `myst.yml`.

## Local build

```bash
pip install -r requirements.txt
pip install pre-commit && pre-commit install   # nbstripout removes notebook outputs before commit
jupyter book start --execute                    # preview at http://localhost:3000
jupyter book build --html --execute             # build static HTML in _build/html
```

## M1 crawl and benchmark notebooks

The crawl and benchmark notebooks are maintained in [CodeRepo/src/notebooks](https://github.com/hcmus-arxiv-nhom1/CodeRepo/tree/main/src/notebooks). This book contains the report and result-analysis notebooks.

The final benchmark requires all 20,000 IDs; sample numbers and placeholder CSVs must not be presented as final results. The raw corpus is stored on Drive under `runs/<RUN_ID>/data/corpus/`. Use a separate run ID for smoke tests and restore and verify after runtime loss. Do not commit the corpus to the book.

On Windows, if Node reports `fetch failed` while connecting to Jupyter on localhost, set `$env:NODE_OPTIONS = "--dns-result-order=ipv4first"` in PowerShell and rebuild. The static HTML entry point is `_build/html/index.html`.

## Rules

- **Notebooks contain no saved outputs.** nbstripout removes outputs on commit; CI builds with `--execute`, so figures and tables are generated during compilation.
- **The book reads CSV files from `data/` only**, not the raw corpus. The schema is defined in the code repository's `docs/data_contract.md`.
- The Data Statistics and Performance notebooks read reconciled evidence in `data/m1/final/`; old placeholder CSVs in `data/m1/` are not official results. Recreate the data with `python scripts/collect_final_m1.py --workspace ..` when the workspace contains the required evidence and snapshot, then check `provenance.json` and the QA and measurement limitations.
- When updating real CSVs, include the code repository commit in the commit message, for example `data: update m1 stats from CodeRepo@abc1234`.
- All changes to `main` go through a PR. CODEOWNERS assigns reviewers, the `check` workflow must pass, and the author must not merge their own PR.

## GitHub setup (one-time)

1. Settings → Pages → Source: **GitHub Actions**.
2. Settings → Branches: protect `main`, require one approval and the `check` workflow, and prevent authors from merging their own PRs.
