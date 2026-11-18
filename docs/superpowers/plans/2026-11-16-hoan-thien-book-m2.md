# Plan to complete the M2 book

**Goal:** Update the book with the official M2 results and the new source-comparison QA, making the scope and limitations of each measurement clear.

**Requirements:** https://hcmus-cs-ta.github.io/lab-book/intro-ds/statement/parsing/

**Evidence:** M2 `m2-full-01`; full-table QA `qa-full-01`; source-comparison QA `qa-thien-01` at https://drive.google.com/drive/folders/1f6AsmOwSaq70vcgoRWUsbKZbfrfhI2Ye. The new result has 1,114 papers with source available and 2,407 parsed versions compared; 22,625 parsed versions outside the scope were skipped. Agreement counts: headings 2357, formulas 2147, floats 2352, items 2342. These compare counts per version, not semantic accuracy; one multi-version run is not representative of the whole corpus. Manual review is pending.

## Tasks

- [ ] Verify that `identity.json`, `qa_status.json`, `structure_summary.json` and the detailed CSV all belong to `qa-thien-01`; reconcile totals and rates with `m2-full-01`. Save the required evidence in `data/m2/` following the book convention, with provenance and the Drive link; do not replace the full-table QA evidence.
- [ ] Update `m2/index.md`, `m2/02-data-stats.ipynb` and `m2/04-quality.ipynb` to distinguish full-table QA on 20,000 papers; the multi-Thiên source subset with 1,114 papers with source and 2,407 versions from 1,079 papers compared; the historical sample of 100 papers and 121 versions; and the incomplete human score sheet. Do not describe the source audit as full-corpus or interpret count agreement as accuracy.
- [ ] Generate a table and chart from CSV/JSON at build time showing count agreement for four categories and the number of versions in scope. Explain selection by run, regular expressions and possible count differences without asserting unverified causes. Identify each sample in every caption and title.
- [ ] Review `m2/01-methodology.md` against the code and actual output, especially the statement that versions without TeX have a root in the hierarchy; correct it if needed. Check coverage, before/after deduplication, BBL recovery, time and RAM against the original evidence and TA requirements.
- [ ] Present the historical reading of 30 papers as unscored observations; do not report a score or describe human review as complete. If the group wants a score, a reviewer must fill the score sheet first.
- [ ] Build the entire Jupyter Book using the README, checking notebook execution, links, data and provenance. Reconcile the totals of 20,000 papers, 26,491 versions and 200 shards. Inspect Plotly figures in a browser, including hover, zoom and layout, or clearly state if the environment prevents this.
- [ ] Review the diff, run repository checks and create a PR for the Book owner. Do not rerun the parser, benchmark or full-corpus restore.
